# bs4/replacer.py milestone3

"""Utilities for transforming tags during parsing."""

from __future__ import annotations

from typing import Any, Callable, Mapping, MutableMapping, Optional, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - imported only for type checking
    from .element import Tag


NameTransformer = Callable[["Tag"], str]
AttrsTransformer = Callable[["Tag"], Mapping[str, Any]]
TagTransformer = Callable[["Tag"], None]


class SoupReplacer:
    """Transform tags encountered while parsing a document.

       The original milestone-2 behaviour is still supported through the
       two-argument constructor::

           SoupReplacer("b", "blockquote")

       In milestone 3 you can instead provide callables that operate on the
       actual :class:`bs4.element.Tag` instances that Beautiful Soup creates::

           SoupReplacer(name_xformer=my_name_xformer,
                        attrs_xformer=my_attrs_xformer,
                        xformer=my_side_effect_function)

       ``name_xformer`` and ``attrs_xformer`` should return the replacement name
       or attributes. ``xformer`` may mutate the tag in place and returns ``None``.
       """

    _og: Optional[str]
    _alt: Optional[str]
    _name_xformer: Optional[NameTransformer]
    _attrs_xformer: Optional[AttrsTransformer]
    _xformer: Optional[TagTransformer]

    def __init__(
            self,
            og_tag: Optional[str] = None,
            alt_tag: Optional[str] = None,
            *,
            name_xformer: Optional[NameTransformer] = None,
            attrs_xformer: Optional[AttrsTransformer] = None,
            xformer: Optional[TagTransformer] = None,
    ) -> None:
        simple_mode = og_tag is not None or alt_tag is not None

        if simple_mode:
            if any((name_xformer, attrs_xformer, xformer)):
                raise ValueError(
                    "Positional tag replacement arguments cannot be combined "
                    "with transformer callables."
                )
            if not og_tag or not alt_tag:
                raise ValueError("og_tag and alt_tag must be non-empty")
            self._og = og_tag.lower()
            self._alt = alt_tag.lower()
            self._name_xformer = None
            self._attrs_xformer = None
            self._xformer = None
        else:
            if not any((name_xformer, attrs_xformer, xformer)):
                raise ValueError(
                    "At least one transformer callable must be provided."
                )
            self._og = None
            self._alt = None
            self._name_xformer = name_xformer
            self._attrs_xformer = attrs_xformer
            self._xformer = xformer

    # ------------------------------------------------------------------
    # Compatibility helpers for the milestone-2 API
    # ------------------------------------------------------------------
    def preprocess_name(self, name: str) -> str:
        """Return the tag name that should be used when creating a tag."""

        if self._og is not None and name and name.lower() == self._og:
            return self._alt  # type: ignore[return-value]
        return name

    def replace(self, name: str) -> str:
        """Backward-compatible alias for :meth:`preprocess_name`."""

        return self.preprocess_name(name)

    # ------------------------------------------------------------------
    # New milestone-3 behaviour
    # ------------------------------------------------------------------
    def apply(self, tag: "Tag") -> None:
        """Apply the configured transformers to ``tag``."""

        if self._og is not None:
            if tag.name and tag.name.lower() == self._og:
                tag.name = self._alt  # type: ignore[assignment]
            return

        if self._name_xformer is not None:
            new_name = self._name_xformer(tag)
            if new_name:
                tag.name = new_name

        if self._attrs_xformer is not None:
            new_attrs = self._attrs_xformer(tag)
            if new_attrs is not None and new_attrs is not tag.attrs:
                tag.attrs.clear()
                if isinstance(new_attrs, MutableMapping):
                    tag.attrs.update(new_attrs)
                else:
                    tag.attrs.update(dict(new_attrs))

        if self._xformer is not None:
            self._xformer(tag)
