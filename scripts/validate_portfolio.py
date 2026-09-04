from __future__ import annotations

import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"


class PortfolioParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.images: list[str] = []
        self.local_links: list[str] = []
        self.h1_count = 0
        self.title_seen = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "img" and values.get("src"):
            self.images.append(values["src"] or "")
        if tag == "a" and values.get("href"):
            href = values["href"] or ""
            parsed = urlparse(href)
            if not parsed.scheme and not parsed.netloc and href and not href.startswith("#"):
                self.local_links.append(parsed.path)
        if tag == "h1":
            self.h1_count += 1
        if tag == "title":
            self.title_seen = True


def main() -> int:
    if not INDEX.exists():
        print("ERROR: index.html is missing")
        return 1

    parser = PortfolioParser()
    parser.feed(INDEX.read_text(encoding="utf-8"))
    errors: list[str] = []

    if parser.h1_count != 1:
        errors.append(f"expected exactly one H1, found {parser.h1_count}")
    if not parser.title_seen:
        errors.append("missing <title>")

    for raw in parser.images + parser.local_links:
        if not raw:
            continue
        target = (ROOT / raw).resolve()
        if ROOT not in target.parents and target != ROOT:
            errors.append(f"local path escapes repository: {raw}")
        elif not target.exists():
            errors.append(f"missing local asset: {raw}")

    readme = ROOT / "README.md"
    if not readme.exists() or "Featured Engineering Projects" not in readme.read_text(encoding="utf-8"):
        errors.append("README portfolio section is missing")

    profile_draft = ROOT / "PROFILE_README.md"
    if not profile_draft.exists():
        errors.append("PROFILE_README.md is missing")

    if errors:
        print("Portfolio validation failed:")
        for error in errors:
            print(f" - {error}")
        return 1

    print("Portfolio integrity validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
