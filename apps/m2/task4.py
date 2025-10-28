#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
task4.py
------------------------------------
Milestone 2 — Part 1 — Task 4

Objective:
  Print out all the tags that have an id attribute, efficiently:
  - Use SoupStrainer so only nodes with 'id' are built during parsing.
  - Retrieve them with a SINGLE API call.

Usage:
  python task4.py <URL or local HTML/XML file>

Examples:(file from https://archive.org/download/stackexchange/askubuntu.com.7z)
  python task4.py https://www.w3schools.com/html/html_id.asp
  python task4.py /Users/shaw/Downloads/askubuntu.com/Posts.xml

Dependencies:
  - beautifulsoup4  (no extra packages required)
------------------------------------
"""

import sys, os, re
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from urllib.request import urlopen
from bs4 import BeautifulSoup, SoupStrainer

def read_bytes_and_parser(src: str):
    if src.startswith(("http://", "https://")):
        print(f"[Info] Fetching from URL: {src}")
        with urlopen(src) as r:
            return r.read(), "html.parser"   # URL -> HTML 解析
    if os.path.exists(src):
        print(f"[Info] Reading local file: {src}")
        with open(src, "rb") as f:
            return f.read(), "xml"           # 本地 -> XML 解析
    print("[Error] Invalid input. Provide a valid URL or file path.")
    sys.exit(1)

def main():
    if len(sys.argv) != 2:
        print("Usage: python task4.py <URL or local HTML/XML file>")
        sys.exit(1)

    source = sys.argv[1]
    data, parser = read_bytes_and_parser(source)

    # 解析阶段：只构建“有 id 属性”的节点（SoupStrainer 自带属性过滤）
    strainer = SoupStrainer(True, id=True)
    soup = BeautifulSoup(data, parser, parse_only=strainer)

    # 单次 API 调用：用正则确保 id 至少含一个非空白字符（非空）
    tags = soup.find_all(True, id=re.compile(r"\S"))

    print(f"[OK] Parsed with {parser}. Found {len(tags)} tag(s) with non-empty id:\n")
    for i, tag in enumerate(tags, 1):
        print(f"{i}. <{tag.name} id='{tag.get('id','')}'>")
    print("\n[Done] Printed tags whose id is NON-EMPTY via SoupStrainer + single API call.")

if __name__ == "__main__":
    main()

