# bs4/replacer.py milestone2part3

class SoupReplacer:
    """Replace a specific tag name during parsing: og_tag -> alt_tag."""
    def __init__(self, og_tag, alt_tag):
        if not og_tag or not alt_tag:
            raise ValueError("og_tag and alt_tag must be non-empty")
        self._og = og_tag.lower()
        self._alt = alt_tag.lower()

    def replace(self, name: str) -> str:
        if name and name.lower() == self._og:
            return self._alt
        return name