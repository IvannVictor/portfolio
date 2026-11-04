"""Valida o artefato real que será enviado ao GitHub Pages (sem rede)."""
from __future__ import annotations

import argparse
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

SITE_PREFIX = "https://ivannvictor.github.io/portfolio/"
REQUIRED = (
    "index.html",
    "sitemap.xml",
    "curriculos/operacoes.html",
    "curriculos/tecnologia.html",
    "curriculos/fiscal-contabil.html",
    "curriculos/liquid-glass.css",
)


class References(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        for key in ("href", "src", "poster", "data"):
            if attrs.get(key):
                self.refs.append((tag, key, attrs[key]))


def validate(root: Path) -> list[str]:
    errors = []
    root = root.resolve()
    for relative in REQUIRED:
        if not (root / relative).is_file():
            errors.append(f"Arquivo obrigatório ausente: {relative}")

    sitemap = root / "sitemap.xml"
    if sitemap.is_file():
        try:
            tree = ET.parse(sitemap)
            locs = [node.text or "" for node in tree.findall(
                ".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc"
            )]
            if not locs or len(locs) != len(set(locs)):
                errors.append("Sitemap vazio ou com URLs duplicadas")
            for loc in locs:
                if not loc.startswith(SITE_PREFIX):
                    errors.append(f"URL fora do domínio esperado no sitemap: {loc}")
                    continue
                path = unquote(urlsplit(loc).path.removeprefix("/portfolio/"))
                destination = root / path
                if destination.is_dir():
                    destination /= "index.html"
                if not destination.is_file():
                    errors.append(f"URL do sitemap não publicada: {loc}")
        except ET.ParseError as exc:
            errors.append(f"Sitemap XML inválido: {exc}")

    pages = sorted(root.rglob("*.html"))
    if not pages:
        errors.append("Nenhuma página HTML no artefato")
    parsed = {}
    for page in pages:
        parser = References()
        parser.feed(page.read_text(encoding="utf-8"))
        parsed[page.resolve()] = parser

    for page, parser in parsed.items():
        for tag, key, ref in parser.refs:
            if ref.startswith(("mailto:", "tel:", "javascript:", "data:", "//")):
                continue
            parts = urlsplit(ref)
            if parts.scheme or parts.netloc:
                continue
            relative = unquote(parts.path)
            if relative.startswith("/"):
                # O site está hospedado no subcaminho /portfolio/.
                if not relative.startswith("/portfolio/"):
                    errors.append(f"{page.relative_to(root)}: caminho absoluto incorreto: {ref}")
                    continue
                destination = root / relative.removeprefix("/portfolio/")
            else:
                destination = page.parent / relative if relative else page
            destination = destination.resolve()
            if not destination.is_relative_to(root):
                errors.append(f"{page.relative_to(root)}: referência fora do site: {ref}")
                continue
            if destination.is_dir():
                destination /= "index.html"
            if not destination.is_file():
                errors.append(f"{page.relative_to(root)}: recurso ausente: {ref}")
                continue
            if parts.fragment and destination.suffix.lower() == ".html":
                target = parsed.get(destination)
                if target and unquote(parts.fragment) not in target.ids:
                    errors.append(f"{page.relative_to(root)}: âncora ausente: {ref}")
    return errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("site", type=Path, help="Diretório _site produzido pelo build")
    args = parser.parse_args()
    failures = validate(args.site)
    for failure in failures:
        print("FAIL:", failure)
    if failures:
        raise SystemExit(f"{len(failures)} falha(s) no artefato de publicação")
    print("PASS: sitemap, arquivos obrigatórios e referências locais do artefato")
