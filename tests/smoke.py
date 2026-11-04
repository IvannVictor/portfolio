"""Functional smoke checks. Requires Playwright and a local Chromium executable."""
import argparse
import functools
import http.server
import os
from pathlib import Path
import shutil
import threading

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


def check(axe_path=None):
    chromium = os.environ.get("CHROMIUM_PATH") or shutil.which("chromium")
    if not chromium:
        raise SystemExit("Chromium not found. Set CHROMIUM_PATH to its executable.")
    handler = functools.partial(QuietHandler, directory=str(ROOT))
    with http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler) as server:
        threading.Thread(target=server.serve_forever, daemon=True).start()
        url = f"http://127.0.0.1:{server.server_port}/"
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(
                    executable_path=chromium, args=["--no-sandbox"]
                )
                try:
                    page = browser.new_page()
                    errors, failed_resources = [], []
                    page.on("pageerror", lambda error: errors.append(str(error)))
                    page.on(
                        "response",
                        lambda response: failed_resources.append(response.url)
                        if response.status >= 400 else None,
                    )
                    page.route(
                        "**/*",
                        lambda route: route.continue_()
                        if route.request.url.startswith(url) else route.abort(),
                    )
                    for width in (320, 390, 760, 768, 1024, 1440):
                        page.set_viewport_size({"width": width, "height": 900})
                        page.goto(url, wait_until="networkidle")
                        assert page.evaluate(
                            "document.documentElement.scrollWidth <= innerWidth"
                        ), f"Horizontal overflow at {width}px"
                        expect(page.locator(".hero .button")).to_be_visible()
                        expect(page.locator(".project")).to_have_count(6)
                        assert page.evaluate("""() => [...document.querySelectorAll('a[href^="#"]')]
                            .every(a => a.hash.length > 1 && document.getElementById(a.hash.slice(1)))""")
                        for image in page.locator("img").all():
                            image.scroll_into_view_if_needed()
                            image.evaluate("image => image.decode()")
                        if axe_path:
                            page.add_script_tag(path=str(axe_path))
                            result = page.evaluate("""async () => await axe.run(document, {
                                runOnly: {type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21aa']}
                            })""")
                            assert not result["violations"], result["violations"]
                        print(f"PASS: {width}px, images, anchors and layout"
                              + (", axe WCAG A/AA" if axe_path else ""))

                    # v3.3: metadados de SEO e compartilhamento social
                    expect(page.locator('link[rel="canonical"]')).to_have_attribute(
                        "href", "https://ivannvictor.github.io/portfolio/"
                    )
                    expect(page.locator('meta[name="description"]')).to_have_count(1)
                    expect(page.locator('meta[property="og:image"]')).to_have_count(1)
                    expect(page.locator('meta[name="twitter:image"]')).to_have_count(1)
                    expect(page.locator('html')).to_have_attribute("lang", "pt-BR")
                    expect(page.locator('meta[name="twitter:title"]')).to_have_count(1)
                    expect(page.locator('meta[name="twitter:description"]')).to_have_count(1)
                    expect(page.locator('meta[property="og:url"]')).to_have_attribute(
                        "content", "https://ivannvictor.github.io/portfolio/"
                    )
                    expect(page.locator('meta[name="twitter:card"]')).to_have_attribute(
                        "content", "summary"
                    )
                    expect(page.locator('link[rel="preload"][as="image"]')).to_have_attribute(
                        "href", "images/victor-profile.webp"
                    )
                    expect(page.locator('img[loading="lazy"]:not([decoding="async"])')).to_have_count(0)
                    # v3.2: navegação acessível e cartões de estudo íntegros
                    expect(page.locator(".project-jump a")).to_have_count(2)
                    assert page.locator(".project-jump a").evaluate_all("(links) => links.every(link => document.querySelector(link.getAttribute(\'href\')))")
                    expect(page.locator("#projetos-profissionais")).to_have_count(1)
                    expect(page.locator("#projetos-estudo")).to_have_count(1)
                    expect(page.locator(".study-card")).to_have_count(3)
                    expect(page.locator(".study-card .study-capability")).to_have_count(3)
                    expect(page.locator(".study-card .demo-link")).to_have_count(3)
                    page.set_viewport_size({"width": 390, "height": 844})
                    page.goto(url)
                    toggle = page.get_by_role("button", name="Menu")
                    navigation = page.get_by_role("navigation", name="Navegação principal")
                    expect(navigation).to_be_hidden()
                    toggle.focus()
                    page.keyboard.press("Enter")
                    expect(navigation).to_be_visible()
                    page.keyboard.press("Tab")
                    expect(navigation.locator("a").first).to_be_focused()
                    page.keyboard.press("Escape")
                    expect(navigation).to_be_hidden()
                    expect(toggle).to_be_focused()
                    toggle.click()
                    navigation.get_by_role("link", name="Projetos").click()
                    expect(page).to_have_url(url + "#projetos")
                    expect(navigation).to_be_hidden()
                    expect(page.locator("#projetos")).to_be_focused()
                    toggle.click()
                    page.set_viewport_size({"width": 1024, "height": 900})
                    expect(navigation).to_be_visible()
                    page.set_viewport_size({"width": 390, "height": 844})
                    expect(navigation).to_be_hidden()
                    print("PASS: menu keyboard, Escape, focus and resize")

                    page.locator("#email").fill("invalid-email")
                    assert not page.locator("#email").evaluate("e => e.checkValidity()")
                    assert not page.locator("form").evaluate("e => e.checkValidity()")
                    page.locator("#nome").fill("Teste local")
                    page.locator("#email").fill("teste@example.com")
                    page.locator("#mensagem").fill("Mensagem de teste local, sem envio.")
                    assert page.locator("form").evaluate("e => e.checkValidity()")
                    page.evaluate("""document.querySelector('form').addEventListener('submit', e => {
                        e.preventDefault(); e.stopImmediatePropagation();
                        window.submitted = Object.fromEntries(new FormData(e.target));
                    }, true)""")
                    page.get_by_role("button", name="Enviar mensagem").click()
                    assert page.evaluate("window.submitted.email") == "teste@example.com"
                    expect(page.locator("form")).to_have_attribute(
                        "action", "https://formspree.io/f/myeelkay"
                    )
                    print("PASS: native form validation and intercepted submission (not sent)")

                    if axe_path:
                        page.add_script_tag(path=str(axe_path))
                    expect(page.locator(".gallery-link")).to_have_count(7)
                    for width in (390, 1440):
                        page.set_viewport_size({"width": width, "height": 900})
                        image_link = page.locator(".gallery-link").first
                        image_link.focus()
                        page.keyboard.press("Enter")
                        dialog = page.get_by_role("dialog")
                        expect(dialog).to_be_visible()
                        expect(dialog.get_by_role("heading")).to_have_text("Central de Impressão")
                        expect(dialog.get_by_role("button", name="Fechar")).to_be_focused()
                        dialog.locator("img").evaluate("image => image.decode()")
                        if axe_path:
                            result = page.evaluate("""async () => await axe.run(document, {
                                runOnly: {type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21aa']}
                            })""")
                            assert not result["violations"], result["violations"]
                        page.keyboard.press("Escape")
                        expect(dialog).to_be_hidden()
                        expect(image_link).to_be_focused()
                        image_link.click()
                        dialog.get_by_role("button", name="Fechar").click()
                        expect(dialog).to_be_hidden()
                        expect(image_link).to_be_focused()
                        second = page.locator(".gallery-link").nth(1)
                        second.click()
                        expect(dialog.get_by_role("heading")).to_have_text("Produtividade da Expedição")
                        page.keyboard.press("Tab")
                        expect(dialog.locator(".viewer-original")).to_be_focused()
                        page.keyboard.press("Tab")
                        expect(dialog.get_by_role("button", name="Fechar")).to_be_focused()
                        page.keyboard.press("Escape")
                    print("PASS: seven gallery images, modal keyboard, focus restoration and captions")

                    context = browser.new_context(
                        java_script_enabled=False, viewport={"width": 320, "height": 844}
                    )
                    fallback = context.new_page()
                    fallback.goto(url)
                    expect(fallback.get_by_role("navigation", name="Navegação principal")).to_be_visible()
                    expect(fallback.locator('a[href="#projetos"]').first).to_be_visible()
                    expect(fallback.locator(".gallery-link")).to_have_count(7)
                    assert fallback.locator(".gallery-link").first.get_attribute("href").endswith("impressao.png")
                    print("PASS: navigation and image links without JavaScript")
                    reduced = browser.new_context(reduced_motion="reduce")
                    reduced_page = reduced.new_page()
                    reduced_page.goto(url)
                    assert reduced_page.evaluate(
                        "getComputedStyle(document.documentElement).scrollBehavior"
                    ) == "auto"
                    print("PASS: reduced motion preference")
                    assert not errors, errors
                    assert not failed_resources, failed_resources
                    print("PASS: no JavaScript exceptions or failed local resources")
                    if not axe_path:
                        print("NOT RUN: axe accessibility checks (provide --axe FILE)")
                finally:
                    browser.close()
        finally:
            server.shutdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--axe", type=Path, help="Local trusted axe-core JavaScript bundle")
    args = parser.parse_args()
    check(args.axe)
