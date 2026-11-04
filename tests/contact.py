"""Contact integration checks with a mocked provider; never sends email."""
import functools
import http.server
import shutil
import threading
from urllib.parse import parse_qs, urlsplit

from playwright.sync_api import expect, sync_playwright
from smoke import ROOT, QuietHandler


def fill(page):
    page.locator('#nome').fill('Teste local')
    page.locator('#email').fill('teste@example.com')
    page.locator('#mensagem').fill('Mensagem de teste sem envio externo.')


def check():
    handler = functools.partial(QuietHandler, directory=str(ROOT))
    with http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler) as server:
        threading.Thread(target=server.serve_forever, daemon=True).start()
        base = f'http://127.0.0.1:{server.server_port}/'
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(executable_path=shutil.which('chromium'), args=['--no-sandbox'])
                try:
                    page = browser.new_page()
                    requests = []
                    def guard(route):
                        if route.request.url.startswith(base):
                            route.continue_()
                        else:
                            if route.request.url != 'https://static.cloudflareinsights.com/beacon.min.js':
                                requests.append(route.request.url)
                            route.abort()
                    page.route('**/*', guard)
                    def fallback_html(route):
                        response = route.fetch()
                        route.fulfill(response=response, body=response.text().replace(
                            'action="https://formspree.io/f/myeelkay"',
                            'action="mailto:iivanvictor@outlook.com"'))
                    page.route(base, fallback_html)
                    page.goto(base)
                    fill(page)
                    page.get_by_role('button', name='Preparar e-mail').click()
                    expect(page.locator('#contact-status')).to_contain_text('ainda não enviada')
                    url = page.locator('#prepared-email').get_attribute('href')
                    assert urlsplit(url).path == 'iivanvictor@outlook.com'
                    assert 'teste@example.com' in parse_qs(urlsplit(url).query)['body'][0]
                    expect(page.locator('#mensagem')).to_have_value('Mensagem de teste sem envio externo.')
                    page.locator('#mensagem').fill('Mensagem atualizada')
                    expect(page.locator('#prepared-email')).to_be_hidden()
                    assert not requests, requests
                    print('PASS: email preparation, recipient, stale-link invalidation; nothing sent')

                    for mode in ('success', 'validation', 'network', 'malformed'):
                        def provider(route):
                            requests.append(mode)
                            assert route.request.method == 'POST'
                            assert 'teste@example.com' in route.request.post_data
                            if mode == 'network':
                                route.abort()
                            elif mode == 'validation':
                                route.fulfill(status=422, json={'errors': [{'message': 'Rejected'}]})
                            elif mode == 'malformed':
                                route.fulfill(status=200, content_type='text/html', body='unusable response')
                            else:
                                route.fulfill(status=200, json={'ok': True})
                        page.route('https://formspree.io/f/myeelkay', provider)
                        page.goto(base + 'index.html')
                        fill(page)
                        page.get_by_role('button', name='Enviar mensagem').click()
                        if mode == 'success':
                            expect(page.locator('#contact-status')).to_contain_text('aceita pelo serviço')
                            expect(page.locator('#mensagem')).to_have_value('')
                            expect(page.locator('#prepared-email')).to_be_hidden()
                        else:
                            expect(page.locator('#contact-status')).to_contain_text('Não foi possível confirmar')
                            expect(page.locator('#mensagem')).to_have_value('Mensagem de teste sem envio externo.')
                            expect(page.locator('#prepared-email')).to_be_visible()
                        expect(page.get_by_role('button', name='Enviar mensagem')).to_be_enabled()
                        page.unroute('https://formspree.io/f/myeelkay', provider)
                        print(f'PASS: mocked provider {mode}')
                    assert requests == ['success', 'validation', 'network', 'malformed'], requests
                    context = browser.new_context(java_script_enabled=False)
                    fallback = context.new_page()
                    fallback.goto(base + 'index.html')
                    expect(fallback.locator('form')).to_have_attribute('action', 'https://formspree.io/f/myeelkay')
                    expect(fallback.locator('form')).to_have_attribute('method', 'post')
                    expect(fallback.get_by_role('button', name='Enviar mensagem')).to_be_enabled()
                    context.close()
                    print('PASS: native HTML POST fallback without JavaScript')
                    print('PASS: all external submissions mocked; no real mail sent')
                finally:
                    browser.close()
        finally:
            server.shutdown()


if __name__ == '__main__':
    check()
