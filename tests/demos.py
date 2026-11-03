"""Functional checks for the local demos, including a subdirectory deployment."""
import argparse
import functools
import http.server
import os
from pathlib import Path
import shutil
import threading

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class SubdirectoryHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if not self.path.startswith('/portfolio/'):
            self.send_error(404)
            return
        self.path = self.path[len('/portfolio'):]
        try:
            super().do_GET()
        except (BrokenPipeError, ConnectionResetError):
            # The browser may cancel an image request during navigation.
            pass

    def log_message(self, *_args):
        pass


def check(axe=None):
    handler = functools.partial(SubdirectoryHandler, directory=str(ROOT))
    with http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler) as server:
        threading.Thread(target=server.serve_forever, daemon=True).start()
        base = f'http://127.0.0.1:{server.server_port}/portfolio/'
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    executable_path=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium'),
                    args=['--no-sandbox'],
                )
                try:
                    page = browser.new_page()
                    errors, missing, remote, posts = [], [], [], []
                    page.on('pageerror', lambda e: errors.append(str(e)))
                    page.on('response', lambda r: missing.append(r.url) if r.status >= 400 else None)
                    page.on('request', lambda r: posts.append(r.url) if r.method == 'POST' else None)
                    def route(request):
                        if request.request.url.startswith(base):
                            request.continue_()
                        else:
                            remote.append(request.request.url)
                            request.abort()
                    page.route('**/*', route)
                    for slug in ('pokedex', 'tarefas', 'login'):
                        for width in (320, 390, 768, 1440):
                            page.set_viewport_size({'width': width, 'height': 900})
                            page.goto(base + f'demos/{slug}/index.html', wait_until='networkidle')
                            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), (slug, width)
                            for image in page.locator('img').all():
                                image.evaluate('image => image.decode()')
                            expect(page.locator('.demo-banner a')).to_have_attribute('href', '../../index.html#projetos')
                            if axe:
                                page.add_script_tag(path=str(axe))
                                result = page.evaluate("""async () => await axe.run(document, {
                                    runOnly: {type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21aa']}
                                })""")
                                assert not result['violations'], (slug, width, result['violations'])
                        print(f'PASS: {slug}, four widths, local assets and subdirectory paths' + (', axe A/AA' if axe else ''))

                    page.goto(base + 'index.html')
                    expect(page.locator('.demo-link')).to_have_count(3)
                    page.locator('.demo-link').first.click()
                    expect(page.locator('.cartao-pokemon')).to_have_count(10)
                    theme = page.get_by_role('button', name='Alternar tema')
                    theme.focus()
                    page.keyboard.press('Enter')
                    expect(theme).to_have_attribute('aria-pressed', 'true')
                    assert page.locator('body').evaluate("e => e.classList.contains('modo-escuro')")
                    theme.click()
                    expect(theme).to_have_attribute('aria-pressed', 'false')
                    page.locator('.demo-banner a').click()
                    expect(page).to_have_url(base + 'index.html#projetos')
                    print('PASS: portfolio-to-demo round trip and theme keyboard toggle')

                    page.goto(base + 'demos/tarefas/index.html')
                    page.evaluate('localStorage.clear()')
                    page.reload(wait_until="networkidle")
                    field = page.get_by_label('Nova tarefa')
                    field.fill('   ')
                    page.get_by_role('button', name='Adicionar').click()
                    expect(page.locator('.task')).to_have_count(0)
                    payload = '<img src=x onerror="window.injected=true">'
                    field.fill(payload)
                    field.press('Enter')
                    expect(page.locator('.task p')).to_have_text(payload)
                    expect(page.locator('.task img')).to_have_count(0)
                    assert page.evaluate('window.injected !== true')
                    page.reload(wait_until="networkidle")
                    expect(page.locator('.task')).to_have_count(1)
                    toggle = page.locator('.task button').first
                    toggle.focus()
                    page.keyboard.press('Enter')
                    expect(page.locator('.task')).to_have_class('task done')
                    page.reload(wait_until="networkidle")
                    expect(page.locator('.task')).to_have_class('task done')
                    page.locator('.task button').last.click()
                    expect(page.locator('.task')).to_have_count(0)
                    page.evaluate("localStorage.setItem('portfolio.demo.tasks.v1','broken JSON')")
                    page.reload(wait_until="networkidle")
                    expect(page.get_by_role('status')).to_contain_text('Não foi possível recuperar')
                    page.evaluate("() => { Storage.prototype.setItem = () => { throw new Error('QuotaExceededError') }; }")
                    field.fill('Tarefa em memória')
                    field.press('Enter')
                    expect(page.locator('.task')).to_have_count(1)
                    expect(page.get_by_role('status')).to_contain_text('não permitiu salvar')
                    print('PASS: task CRUD, persistence, literal user text, empty/corrupt/quota handling')

                    page.goto(base + 'demos/login/index.html')
                    page.get_by_role('button', name='Experimentar interface').click()
                    assert not page.locator('form').evaluate('e => e.checkValidity()')
                    page.get_by_label('Usuário').fill('usuario-ficticio')
                    page.get_by_label('Senha', exact=True).fill('senha-ficticia')
                    page.get_by_label('Senha', exact=True).press('Enter')
                    expect(page.get_by_role('status')).to_contain_text('Nenhuma autenticação')
                    expect(page.get_by_label('Senha', exact=True)).to_have_value('')
                    assert not posts, posts
                    assert not remote, remote
                    assert not missing, missing
                    assert not errors, errors
                    fallback_context = browser.new_context(java_script_enabled=False)
                    fallback = fallback_context.new_page()
                    fallback.goto(base + 'demos/login/index.html')
                    expect(fallback.get_by_label('Usuário')).to_be_disabled()
                    expect(fallback.get_by_label('Senha', exact=True)).to_be_disabled()
                    expect(fallback.get_by_role('button', name='Experimentar interface')).to_be_disabled()
                    fallback_context.close()
                    print('PASS: login demonstration without credential transmission or persistence')
                    print('PASS: no remote requests, missing assets or JavaScript exceptions')
                    if not axe:
                        print('NOT RUN: axe accessibility checks (provide --axe FILE)')
                finally:
                    browser.close()
        finally:
            server.shutdown()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--axe', type=Path)
    check(parser.parse_args().axe)
