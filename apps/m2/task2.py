#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
task2.py
------------------------------------
Milestone 2 — Task 2

Objective:
    Reimplement Milestone 1 — Task 2 using BeautifulSoup's SoupStrainer.
    - If input is a local XML file: print all <row> tags.
    - If input is a URL: print all <link> tags.

Usage:
    python task2.py <URL or local XML file>
    
Examples:(file from https://archive.org/download/stackexchange/askubuntu.com.7z)
    python task2.py /Users/shaw/Downloads/askubuntu.com/Posts.xml
    python task2.py https://www.w3.org/TR/html401/struct/links.html

Dependencies:
    - beautifulsoup4
------------------------------------
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from urllib.request import urlopen
from bs4 import BeautifulSoup, SoupStrainer


def read_data(source):
    """Read data from URL or local file."""
    if source.startswith(("http://", "https://")):
        print(f"[Info] Fetching from URL: {source}")
        try:
            with urlopen(source) as response:
                return response.read(), "html.parser"
        except Exception as e:
            print(f"[Error] Failed to fetch the URL: {e}")
            sys.exit(1)
    elif os.path.exists(source):
        print(f"[Info] Reading from local file: {source}")
        try:
            with open(source, "rb") as f:
                return f.read(), "xml"
        except Exception as e:
            print(f"[Error] Failed to read file: {e}")
            sys.exit(1)
    else:
        print("[Error] Invalid input. Provide a valid URL or file path.")
        sys.exit(1)


def main():
    if len(sys.argv) != 2:
        print("Usage: python task2.py <URL or local XML file>")
        sys.exit(1)

    source = sys.argv[1]
    data, parser = read_data(source)

    # 自动选择目标标签
    target_tag = "row" if parser == "xml" else "link"
    print(f"[Info] Parsing only <{target_tag}> tags using SoupStrainer ({parser}) ...")

    # 使用 SoupStrainer，仅解析目标标签
    strainer = SoupStrainer(target_tag)
    soup = BeautifulSoup(data, parser, parse_only=strainer)

    tags = soup.find_all(target_tag)
    print(f"[OK] Found {len(tags)} <{target_tag}> tag(s) in the document:\n")

    for idx, tag in enumerate(tags, start=1):
        print(f"{idx}. {tag}")

    print(f"\n[Done] All <{target_tag}> tags printed successfully.")


if __name__ == "__main__":
    main()
