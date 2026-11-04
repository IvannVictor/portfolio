"""Monta exatamente o mesmo artefato para CI e GitHub Pages."""
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "_site"
FILES = ("index.html", "sitemap.xml", "robots.txt")
DIRS = ("css", "js", "images", "demos", "curriculos")


def build():
    if DEST.exists():
        shutil.rmtree(DEST)
    DEST.mkdir()
    for name in FILES:
        shutil.copy2(ROOT / name, DEST / name)
    for name in DIRS:
        shutil.copytree(ROOT / name, DEST / name)
    print("Artefato preparado:", DEST)


if __name__ == "__main__":
    build()
