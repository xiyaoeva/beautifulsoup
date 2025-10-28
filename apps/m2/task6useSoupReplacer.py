#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Milestone 2 — Part 3 — Task 6
-----------------------------------------------------
Change all <b> tags to <blockquote> tags DURING parsing
using the SoupReplacer API, and write the resulting tree
into an output file.

Usage:
  python task6useSoupReplacer.py <URL or local HTML file>

Example:
  python task6useSoupReplacer.py https://www.w3schools.com/tags/tag_b.asp
-----------------------------------------------------
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))) 
from urllib.request import urlopen
from bs4 import BeautifulSoup, SoupReplacer   # 关键：调用你的 SoupReplacer

def read_source(src: str) -> bytes:
    """Read HTML bytes from URL or local file."""
    if src.startswith(("http://", "https://")):
        print(f"[Info] Fetching from URL: {src}")
        with urlopen(src) as resp:
            return resp.read()
    elif os.path.exists(src):
        print(f"[Info] Reading local file: {src}")
        with open(src, "rb") as f:
            return f.read()
    else:
        print("[Error] Invalid source path or URL.")
        sys.exit(1)

def main():
    if len(sys.argv) != 2:
        print("Usage: python task6useSoupReplacer.py <URL or local HTML file>")
        sys.exit(1)

    src = sys.argv[1]
    html_bytes = read_source(src)

    # 在解析阶段使用 SoupReplacer
    replacer = SoupReplacer("b", "blockquote")
    soup = BeautifulSoup(html_bytes, "html.parser", replacer=replacer)

    output_path = os.path.join(os.path.dirname(__file__), "task6_output.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(soup.prettify())

    print("[Success] <b> tags replaced with <blockquote> tags during parsing.")
    print(f"[Output] Written to {output_path}")

if __name__ == "__main__":
    main()



