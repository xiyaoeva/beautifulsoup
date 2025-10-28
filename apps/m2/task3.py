#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
task3.py
------------------------------------
Milestone 2 — Part 1 — Task 3

Objective:
    Print out all the tags in the document, using BeautifulSoup's SoupStrainer
    so that only tag nodes are parsed (skip text/comments/etc).

Usage:
    python task3.py <URL or local HTML/XML file>

Examples:(file from https://archive.org/download/stackexchange/askubuntu.com.7z)
    python task3.py /Users/shaw/Downloads/askubuntu.com/Posts.xml
    python task3.py https://www.w3.org/TR/html401/struct/links.html

Dependencies:
    - beautifulsoup4  (no extra packages required)
------------------------------------
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from urllib.request import urlopen
from bs4 import BeautifulSoup, SoupStrainer


def read_bytes(src: str) -> bytes:
    """Read HTML/XML bytes from URL or local path."""
    if src.startswith(("http://", "https://")):
        print(f"[Info] Fetching from URL: {src}")
        with urlopen(src) as r:
            return r.read(), "html.parser"   # 网页 → HTML 解析器
    if os.path.exists(src):
        print(f"[Info] Reading local file: {src}")
        with open(src, "rb") as f:
            return f.read(), "xml"           # 本地文件 → XML 解析器
    print("[Error] Invalid input. Provide a valid URL or file path.")
    sys.exit(1)


def main():
    if len(sys.argv) != 2:
        print("Usage: python task3.py <URL or local HTML/XML file>")
        sys.exit(1)

    source = sys.argv[1]
    data, parser = read_bytes(source)

    # 使用 SoupStrainer：只解析标签节点（跳过文本、注释）
    strainer = SoupStrainer(lambda name, attrs=None: name is not None)

    soup = BeautifulSoup(data, parser, parse_only=strainer)

    # 找出所有标签并打印
    all_tags = soup.find_all(True)
    print(f"[OK] Parsed with {parser}. Found {len(all_tags)} tag occurrence(s):\n")

    for i, tag in enumerate(all_tags, 1):
        print(f"{i}. <{tag.name}>")

    # 输出唯一标签集合
    unique = sorted({t.name for t in all_tags})
    print(f"\n[Summary] Unique tag names ({len(unique)}): {', '.join(unique)}")

    print("\n[Done] Printed all tags via SoupStrainer.")


if __name__ == "__main__":
    main()
