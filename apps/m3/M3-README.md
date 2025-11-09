# Milestone-3

## New test cases to test API
```bash
python test_replacer.py
```

## Application: Milestone-1 Task 7

```bash
python task7_use_soup_replacer.py https://www.w3schools.com/html/html_paragraphs.asp
```
The output HTML is written to `apps/m3/task7_output.html`.

## Technical brief: Milestone-2 vs Milestone-3 SoupReplacer

In Milestone-2 the API was very small. You could rename one tag with
`SoupReplacer("old", "new")`, or pass one function that ran on every tag.
Milestone-3 keeps that behaviour, but the new rule registry lets us register
many small rules, choose their order, and stop once one rule runs. This removes
the old `if tag.name == ...` code we wrote by hand, and it is easier to combine
different transformations.

I think we should ship the registry as the main path. It does not break old
code, has only one new entry point (`register_rule`), and it opens useful
scenarios:

* Config files or plugins that list soup changes in a clean way.
* Builder add-ons that ship rules for special formats, like Markdown-to-HTML.
* Tests that check rule order through the public `rules` attribute.

Later we can look at saving rules to disk or linking the API with
`SoupStrainer` to skip tags we do not care about. Even without that, Milestone-3
already turns messy custom functions into a safe and clear tool.