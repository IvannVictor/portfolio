"""Functional smoke checks. Requires Playwright and a local Chromium executable."""
import argparse
import json
import xml.etree.ElementTree as ET
import functools
import http.server
import os
from pathlib import Path
import shutil
import threading

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]

# Evita caracteres de escape literais visíveis no topo da página.
assert r'type="image/svg+xml" />\n' not in (ROOT / "index.html").read_text(encoding="utf-8")


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
                        expect(page.locator('.hero .button[href="#projetos"]')).to_be_visible()
                        expect(page.locator(".project")).to_have_count(6)
                        assert page.evaluate("""() => [...document.querySelectorAll('a[href^="#"]')]
                            .every(a => a.hash.length > 1 && document.getElementById(a.hash.slice(1)))""")
                        for image in page.locator("img").all():
                            image.scroll_into_view_if_needed()
                            image.evaluate("""async image => {
                                if (image.loading === "lazy") image.loading = "eager";
                                try { await image.decode(); }
                                catch (error) { throw new Error(`Image decode failed: ${image.currentSrc || image.src} — ${error.message}`); }
                            }""")
                        if axe_path:
                            page.add_script_tag(path=str(axe_path))
                            result = page.evaluate("""async () => await axe.run(document, {
                                runOnly: {type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21aa']}
                            })""")
                            assert not result["violations"], result["violations"]
                        print(f"PASS: {width}px, images, anchors and layout"
                              + (", axe WCAG A/AA" if axe_path else ""))

                    # v3.7: menu começa recolhido sem deslocar o layout mobile
                    assert page.locator("html.js-enabled").count() == 1
                    if page.viewport_size["width"] <= 760:
                        assert page.locator("#navegacao").is_hidden()
                        page.locator(".menu-toggle").click()
                        assert page.locator("#navegacao").is_visible()
                        page.locator(".menu-toggle").click()
                        assert page.locator("#navegacao").is_hidden()
                    # v3.7: prioridades de rede não competem com a imagem principal
                    expect(page.locator('img[loading="lazy"][fetchpriority="low"]')).to_have_count(9)
                    expect(page.locator('img[loading="lazy"]:not([fetchpriority="low"])')).to_have_count(0)
                    expect(page.locator('img[src="images/victor-profile.webp"]')).to_have_attribute(
                        "fetchpriority", "high"
                    )
                    expect(page.locator('img[src="images/victor-profile.webp"]')).to_have_attribute(
                        "loading", "eager"
                    )
                    assert page.locator('link[rel="stylesheet"]').get_attribute("href").endswith("v=3.9.0")
                    # v3.6: JSON-LD válido, sitemap sem links inexistentes
                    structured = json.loads(page.locator('script[type="application/ld+json"]').text_content())
                    assert structured["@context"] == "https://schema.org"
                    assert structured["@type"] == "Person"
                    assert structured["url"] == "https://ivannvictor.github.io/portfolio/"
                    assert len(structured["sameAs"]) == 2
                    assert structured["image"].endswith("/images/victor-profile.webp")
                    assert (ROOT / "images/victor-profile.webp").is_file()
                    sitemap = ET.parse(ROOT / "sitemap.xml")
                    locs = [node.text for node in sitemap.findall(
                        ".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc"
                    )]
                    assert len(locs) == len(set(locs)) == 8
                    prefix = "https://ivannvictor.github.io/portfolio/"
                    for loc in locs:
                        assert loc.startswith(prefix), loc
                        relative = loc[len(prefix):] or "index.html"
                        assert (ROOT / relative).is_file(), relative
                    # v3.9 etapa 5: somente o beacon oficial, sem eventos de formulário
                    beacon = page.locator('script[src="https://static.cloudflareinsights.com/beacon.min.js"]')
                    expect(beacon).to_have_count(1)
                    assert beacon.get_attribute("type") == "module"
                    assert json.loads(beacon.get_attribute("data-cf-beacon")) == {
                        "token": "cb11bd01f1c04f13ba7f77d34c35f95b"
                    }
                    # v3.3: metadados de SEO e compartilhamento social
                    expect(page.locator('link[rel="canonical"]')).to_have_attribute(
                        "href", "https://ivannvictor.github.io/portfolio/"
                    )
                    expect(page.locator('meta[name="description"]')).to_have_count(1)
                    expect(page.locator('link[rel="icon"][type="image/svg+xml"]')).to_have_attribute("href", "images/ivan-victor-monograma.svg")
                    expect(page.locator('header img[src="images/ivan-victor-monograma.svg"]')).to_have_count(1)
                    expect(page.locator(".hero-brand-watermark")).to_have_count(1)
                    expect(page.locator(".about-signature img")).to_have_count(1)
                    expect(page.locator(".footer-brand img")).to_have_count(1)
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
                    # v3.5: arquitetura acessível e conteúdo operacional verificável
                    expect(page.get_by_role("heading", name="Arquitetura e controles operacionais")).to_have_count(1)
                    expect(page.locator("#zpl-architecture-title ~ .case-pipeline li")).to_have_count(4)
                    expect(page.locator("#zpl-architecture-title ~ .case-pipeline li strong")).to_have_text(
                        ["Entrada", "Tratamento", "Validação", "Saída e consulta"]
                    )
                    page.set_viewport_size({"width": 390, "height": 844})
                    assert page.locator("#zpl-architecture-title ~ .case-pipeline").evaluate(
                        "el => getComputedStyle(el).gridTemplateColumns.split(' ').length"
                    ) == 1
                    page.set_viewport_size({"width": 1440, "height": 900})
                    assert page.locator("#zpl-architecture-title ~ .case-pipeline").evaluate(
                        "el => getComputedStyle(el).gridTemplateColumns.split(' ').length"
                    ) == 2
                    assert "não equivale à confirmação física" in page.locator("#zpl-architecture-title").locator("..").locator(".case-caveat").inner_text()
                    assert "não elimina a conferência" in page.locator(".process-case").text_content()
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
                    expect(toggle).to_have_attribute("aria-expanded", "true")
                    page.keyboard.press("Tab")
                    expect(navigation.locator("a").first).to_be_focused()
                    page.keyboard.press("Escape")
                    expect(navigation).to_be_hidden()
                    expect(toggle).to_have_attribute("aria-expanded", "false")
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
                    # v3.9 etapa 3: estudos de caso verificáveis e acessíveis
                    expect(page.locator("#zpl-architecture-title")).to_have_count(1)
                    expect(page.locator("#omie-architecture-title")).to_have_count(1)
                    expect(page.locator(".case-lead")).to_have_count(2)
                    expect(page.locator(".case-verification")).to_have_count(1)
                    expect(page.locator("#omie-architecture-title ~ .case-pipeline li")).to_have_count(4)
                    expect(page.locator(".case-verification li")).to_have_count(3)
                    print("PASS: case studies, evidence and Omie operational flow")
                    # v3.9: conversão para recrutadores e navegação acessível
                    expect(page.locator('#navegacao a[href="#curriculos"]')).to_have_count(1)
                    expect(page.locator('.hero .button-secondary[href="#curriculos"]')).to_have_count(1)
                    expect(page.locator('.hero-shortcut a[href="#contato"]')).to_have_count(1)
                    expect(page.locator('#curriculos .resume-contact a[href="#contato"]')).to_have_count(1)
                    page.set_viewport_size({"width": 390, "height": 844})
                    page.goto(url, wait_until="networkidle")
                    page.locator(".menu-toggle").click()
                    expect(page.locator('#navegacao a[href="#curriculos"]')).to_be_visible()
                    page.locator('#navegacao a[href="#curriculos"]').click()
                    expect(page.locator("#navegacao")).to_be_hidden()
                    assert page.evaluate("location.hash") == "#curriculos"
                    page.set_viewport_size({"width": 1440, "height": 900})
                    page.goto(url, wait_until="networkidle")
                    page.locator('.hero .button-secondary[href="#curriculos"]').click()
                    assert page.evaluate("location.hash") == "#curriculos"
                    print("PASS: recruiter CTA, mobile menu and resume navigation")
                    # v3.8: três currículos, acessíveis e disponíveis para impressão
                    expect(page.locator("#curriculos .resume-card")).to_have_count(3)
                    for slug in ("operacoes", "tecnologia", "fiscal-contabil"):
                        link = page.locator(f'#curriculos a[href="curriculos/{slug}.html"]')
                        expect(link).to_have_count(1)
                        resume_page = browser.new_page()
                        response = resume_page.goto(url.rstrip("/") + f"/curriculos/{slug}.html")
                        assert response.status == 200, slug
                        expect(resume_page.locator("main h1")).to_have_text("IVAN VICTOR AZEVEDO SILVA")
                        expect(resume_page.get_by_role("button", name="Imprimir / Salvar como PDF")).to_be_visible()
                        assert resume_page.locator("main").inner_text().count("EXPERIÊNCIA PROFISSIONAL") == 1
                        expect(resume_page.locator(".glass-frame .resume-paper")).to_have_count(1)
                        assert resume_page.locator('link[href^="liquid-glass.css"]').count() == 1
                        assert "radial-gradient" in resume_page.locator("body").evaluate(
                            "(el) => getComputedStyle(el).backgroundImage"
                        )
                        for width in (320, 390, 768, 1440):
                            resume_page.set_viewport_size({"width": width, "height": 900})
                            assert resume_page.evaluate(
                                "document.documentElement.scrollWidth <= innerWidth"
                            ), f"Resume overflow {slug}: {width}"
                        resume_page.emulate_media(media="print")
                        assert resume_page.locator(".toolbar").evaluate(
                            "(el) => getComputedStyle(el).display"
                        ) == "none"
                        assert resume_page.locator(".glass-frame").evaluate(
                            "(el) => getComputedStyle(el).backgroundColor"
                        ) == "rgb(255, 255, 255)"
                        resume_page.emulate_media(media="screen")
                        resume_page.close()
                    print("PASS: three resume pages and print actions")
                    print("PASS: navigation and image links without JavaScript")
                    reduced = browser.new_context(reduced_motion="reduce")
                    reduced_page = reduced.new_page()
                    reduced_page.goto(url)
                    assert reduced_page.evaluate(
                        "getComputedStyle(document.documentElement).scrollBehavior"
                    ) == "auto"
                    expect(reduced_page.locator(".reveal-ready")).to_have_count(0)
                    # v3.4: mudança de preferência durante a sessão deve revelar
                    # imediatamente conteúdo ainda não visitado.
                    motion_page = browser.new_page(
                        viewport={"width": 390, "height": 844},
                        reduced_motion="no-preference",
                    )
                    motion_page.goto(url, wait_until="networkidle")
                    motion_page.evaluate("window.scrollTo(0, 0)")
                    motion_page.emulate_media(reduced_motion="reduce")
                    expect(motion_page.locator(".reveal-ready")).to_have_count(0)
                    expect(motion_page.locator("[data-reveal]")).to_have_count(0)
                    assert motion_page.evaluate("""() => [...document.querySelectorAll(".is-visible")]
                        .every(element => getComputedStyle(element).opacity !== "0")""")
                    motion_page.close()
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
