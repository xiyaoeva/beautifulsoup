#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Milestone 3 — Task 7 application using the enhanced SoupReplacer API.

This script mirrors the Milestone-1 task that prettifies an HTML document
after ensuring every ``<p>`` element has ``class="test"``. The mutation is
performed *during parsing* via the Milestone-3 SoupReplacer rule registry so
no post-processing walk is required.

Usage::

    python task7_use_soup_replacer.py <URL or local HTML file>

Examples:
  python task7_use_soup_replacer.py https://www.w3schools.com/html/html_paragraphs.asp

The transformed document is written to ``task7_output.html`` in the same
directory as this script.
"""

from __future__ import annotations

import os
import sys
from typing import Iterable
from urllib.request import urlopen

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from bs4 import BeautifulSoup, SoupReplacer


def read_source(src: str) -> bytes:
    """Read HTML bytes from ``src`` which may be a URL or a local path."""

    if src.startswith(("http://", "https://")):
        print(f"[Info] Fetching from URL: {src}")
        with urlopen(src) as resp:
            return resp.read()

    if os.path.exists(src):
        print(f"[Info] Reading local file: {src}")
        with open(src, "rb") as handle:
            return handle.read()

    raise SystemExit("[Error] Invalid source path or URL.")


def _force_test_class(tag) -> None:
    """Set ``class="test"`` on ``tag`` regardless of its previous value."""

    tag.attrs["class"] = ["test"]


def build_replacer() -> SoupReplacer:
    """Create a SoupReplacer that applies the Milestone-1 Task 7 rule."""

    replacer = SoupReplacer()
    replacer.register_rule(tag_name="p", xformer=_force_test_class, priority=5)
    return replacer


def main(argv: Iterable[str] | None = None) -> None:
    args = list(argv if argv is not None else sys.argv[1:])
    if len(args) != 1:
        print("Usage: python task7_use_soup_replacer.py <URL or local HTML file>")
        raise SystemExit(1)

    src = args[0]
    html_bytes = read_source(src)

    soup = BeautifulSoup(html_bytes, "html.parser", replacer=build_replacer())

    output_path = os.path.join(os.path.dirname(__file__), "task7_output.html")
    with open(output_path, "w", encoding="utf-8") as handle:
        handle.write(soup.prettify())

    print("[Success] Paragraph class attribute enforced during parsing.")
    print(f"[Output] Written to {output_path}")


if __name__ == "__main__":
    main()