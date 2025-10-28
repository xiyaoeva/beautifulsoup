#Milestone2Part3 Xiyao LI

# test_replacer_slim.py
# 仅用标准库做断言
# example用法:python test_replacer.py
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from bs4 import BeautifulSoup, SoupReplacer  # 这是要测的库/代码

def test_basic_replacement():
    html = "<div><b>bold</b> and <i>italic</i></div>"
    replacer = SoupReplacer("b", "blockquote")
    soup = BeautifulSoup(html, "html.parser", replacer=replacer)

    assert soup.find("b") is None
    blk = soup.find("blockquote")
    assert blk is not None and blk.text == "bold"
    assert soup.find("i").text == "italic"

def test_no_replacement_for_other_tags():
    html = "<root><p>Hello</p><em>World</em></root>"
    replacer = SoupReplacer("b", "strong")
    soup = BeautifulSoup(html, "html.parser", replacer=replacer)

    assert soup.find("p") is not None
    assert soup.find("em") is not None
    assert soup.find("b") is None
    assert soup.find("strong") is None

def test_nested_and_multiple():
    # 确认多处与嵌套都被替换
    html = "<div><b>a</b><span><b>b</b></span></div>"
    soup = BeautifulSoup(html, "html.parser", replacer=SoupReplacer("b", "blockquote"))
    assert soup.find("b") is None
    blocks = soup.find_all("blockquote")
    assert len(blocks) == 2 and [t.text for t in blocks] == ["a", "b"]

if __name__ == "__main__":
    try:
        test_basic_replacement()
        test_no_replacement_for_other_tags()
        test_nested_and_multiple()
        print("OK (3 tests)")
        sys.exit(0)
    except AssertionError:
        # 打印更友好的失败码与堆栈
        import traceback
        traceback.print_exc()
        sys.exit(1)
