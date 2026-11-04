"""Teste isolado da demonstração v3.1; não envia dados externos."""
import functools
import http.server
import threading
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass

def test_flow():
    handler = functools.partial(QuietHandler, directory=str(ROOT))
    with http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler) as server:
        threading.Thread(target=server.serve_forever, daemon=True).start()
        base = f"http://127.0.0.1:{server.server_port}/"
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                try:
                    for width in (320, 390, 768, 1440):
                        page = browser.new_page(viewport={"width": width, "height": 900})
                        errors, remote = [], []
                        page.on("pageerror", lambda error: errors.append(str(error)))
                        page.route("**/*", lambda route: route.continue_() if route.request.url.startswith(base) else (remote.append(route.request.url), route.abort()))
                        page.goto(base + "demos/zpl/index.html")
                        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), width
                        expect(page.locator('[aria-current="step"]')).to_have_count(1)
                        expect(page.locator("#previous")).to_be_disabled()
                        for i in range(3):
                            page.locator("#next").click()
                            expect(page.locator('[aria-current="step"]')).to_have_attribute("data-step", str(i + 1))
                        expect(page.locator("#next")).to_be_disabled()
                        assert "não é confirmação" in page.locator("#step-evidence").inner_text() or "não há histórico real" in page.locator("#step-evidence").inner_text()
                        page.locator("#previous").click()
                        expect(page.locator('[aria-current="step"]')).to_have_attribute("data-step", "2")
                        page.locator("#restart").click()
                        expect(page.locator('[aria-current="step"]')).to_have_attribute("data-step", "0")
                        assert not errors, errors
                        assert not remote, remote
                        page.close()
                    nojs = browser.new_context(java_script_enabled=False)
                    fallback = nojs.new_page()
                    fallback.goto(base + "demos/zpl/index.html")
                    expect(fallback.locator("#step-title")).to_contain_text("Recebimento")
                    expect(fallback.get_by_role("link", name="Voltar aos projetos")).to_be_visible()
                    nojs.close()
                finally:
                    browser.close()
        finally:
            server.shutdown()

if __name__ == "__main__":
    test_flow()
    print("PASS: fluxo ZPL v3.1, responsividade, navegação, fallback sem JS e isolamento")
