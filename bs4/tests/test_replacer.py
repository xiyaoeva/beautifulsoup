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


def test_name_transformer_callable():#Milestone3starts
    html = "<div><b>bold</b><i>italic</i></div>"

    replacer = SoupReplacer(
        name_xformer=lambda tag: "blockquote" if tag.name == "b" else tag.name
    )
    soup = BeautifulSoup(html, "html.parser", replacer=replacer)

    assert soup.find("b") is None
    assert [t.name for t in soup.find_all()] == ["div", "blockquote", "i"]
    assert soup.blockquote.text == "bold"


def test_attrs_transformer_callable():
    html = '<div><p class="foo" id="x">content</p></div>'

    def attrs_xformer(tag):
        if tag.name == "p":
            # Return a brand new attribute mapping without the class attribute.
            return {k: v for k, v in tag.attrs.items() if k != "class"}
        return tag.attrs

    replacer = SoupReplacer(attrs_xformer=attrs_xformer)
    soup = BeautifulSoup(html, "html.parser", replacer=replacer)

    p = soup.p
    assert p is not None
    assert "class" not in p.attrs and p["id"] == "x"


def test_side_effect_transformer():
    html = '<div><p class="foo" id="x">content</p></div>'

    def remove_class_attr(tag):
        if "class" in tag.attrs:
            del tag.attrs["class"]

    replacer = SoupReplacer(xformer=remove_class_attr)
    soup = BeautifulSoup(html, "html.parser", replacer=replacer)

    assert "class" not in soup.p.attrs


def test_invalid_constructor_mix():
    try:
        SoupReplacer("b", "blockquote", name_xformer=lambda tag: tag.name)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError when mixing constructors") #Milestone3ends


def test_register_rule_by_tag_name():
    html = "<root><b>bold</b><i>italic</i></root>"
    replacer = SoupReplacer()
    replacer.register_rule(tag_name="b", new_name="strong")

    soup = BeautifulSoup(html, "html.parser", replacer=replacer)

    assert soup.find("b") is None
    strong = soup.find("strong")
    assert strong and strong.text == "bold"


def test_register_rule_constant_attrs():
    html = '<root><p class="lead">text</p></root>'
    replacer = SoupReplacer()
    replacer.register_rule(
        tag_name="p",
        new_attrs={"class": "lead", "data-role": "hero"},
    )

    soup = BeautifulSoup(html, "html.parser", replacer=replacer)

    p = soup.find("p")
    assert p is not None
    assert p["data-role"] == "hero"
    assert "lead" in p.get("class", [])


def test_register_rule_priority():
    html = "<root><b>bold</b></root>"
    replacer = SoupReplacer()
    replacer.register_rule(tag_name="b", new_name="low", priority=1)
    replacer.register_rule(tag_name="b", new_name="high", priority=10)

    soup = BeautifulSoup(html, "html.parser", replacer=replacer)

    assert soup.find("low") is None
    assert soup.find("high") is not None


def test_register_rule_stop_processing():
    html = "<root><b>bold</b></root>"
    replacer = SoupReplacer()
    replacer.register_rule(
        tag_name="b",
        new_name="strong",
        stop_processing=True,
    )
    replacer.register_rule(
        tag_name="strong",
        new_attrs={"data-after": "true"},
    )

    soup = BeautifulSoup(html, "html.parser", replacer=replacer)

    strong = soup.find("strong")
    assert strong is not None
    assert "data-after" not in strong.attrs


def test_register_rule_match_predicate():
    html = '<root><span class="keep">a</span><span>b</span></root>'
    replacer = SoupReplacer()
    replacer.register_rule(
        match=lambda tag: tag.name == "span" and "keep" in (tag.get("class") or []),
        new_attrs={"class": "keep", "data-flag": "1"},
    )

    soup = BeautifulSoup(html, "html.parser", replacer=replacer)

    flagged = soup.find("span", {"data-flag": "1"})
    assert flagged is not None
    assert flagged.text == "a"
    assert soup.find_all("span", {"data-flag": "1"})[0] == flagged
    assert soup.find_all("span")[-1].attrs == {}


def test_from_rules_constructor():
    html = '<root><code data-lang="py">print()</code></root>'
    replacer = SoupReplacer.from_rules(
        {"tag_name": "code", "new_name": "pre", "priority": 5},
        {
            "match": lambda tag: tag.name == "pre",
            "xformer": lambda tag: tag.attrs.setdefault("data-block", "true"),
        },
    )

    soup = BeautifulSoup(html, "html.parser", replacer=replacer)

    pre = soup.find("pre")
    assert pre is not None
    assert pre.get("data-block") == "true"
    assert pre.get("data-lang") == "py"

if __name__ == "__main__":
    try:
        test_basic_replacement()
        test_no_replacement_for_other_tags()
        test_nested_and_multiple()

        test_name_transformer_callable() #Milestone3starts
        test_attrs_transformer_callable()#Milestone3starts
        test_side_effect_transformer() #Milestone3starts
        test_invalid_constructor_mix()#Milestone3starts

        test_register_rule_by_tag_name() #Milestone3starts2
        test_register_rule_constant_attrs() #Milestone3starts2
        test_register_rule_priority() #Milestone3starts2
        test_register_rule_stop_processing()#Milestone3starts2
        test_register_rule_match_predicate() #Milestone3starts2
        test_from_rules_constructor()#Milestone3starts2

        print("OK (13 tests)")
        sys.exit(0)
    except AssertionError:
        # 打印更友好的失败码与堆栈
        import traceback
        traceback.print_exc()
        sys.exit(1)
