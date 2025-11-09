# bs4/replacer.py milestone3

"""Utilities for transforming tags during parsing."""

from __future__ import annotations

from dataclasses import dataclass
from typing import (
    Any,
    Callable,
    Iterable,
    Mapping,
    MutableMapping,
    Optional,
    TYPE_CHECKING,
)

if TYPE_CHECKING:  # pragma: no cover - imported only for type checking
    from .element import Tag


NameTransformer = Callable[["Tag"], str]
AttrsTransformer = Callable[["Tag"], Mapping[str, Any]]
TagTransformer = Callable[["Tag"], None]
MatchPredicate = Callable[["Tag"], bool]


def _match_any(tag: "Tag") -> bool:
    return True


@dataclass
class _ReplacementRule:
    """A single transformation rule executed by :class:`SoupReplacer`."""

    match: MatchPredicate
    name_xformer: Optional[NameTransformer] = None
    attrs_xformer: Optional[AttrsTransformer] = None
    xformer: Optional[TagTransformer] = None
    priority: int = 0
    stop_processing: bool = False

    def applies_to(self, tag: "Tag") -> bool:
        try:
            return self.match(tag)
        except Exception:
            return False

    def apply(self, tag: "Tag") -> bool:
        """Apply this rule to ``tag``.

        :return: ``True`` if later rules should be skipped.
        """

        if not self.applies_to(tag):
            return False

        if self.name_xformer is not None:
            new_name = self.name_xformer(tag)
            if new_name:
                tag.name = new_name

        if self.attrs_xformer is not None:
            new_attrs = self.attrs_xformer(tag)
            if new_attrs is not None and new_attrs is not tag.attrs:
                tag.attrs.clear()
                if isinstance(new_attrs, MutableMapping):
                    tag.attrs.update(new_attrs)
                else:
                    tag.attrs.update(dict(new_attrs))

        if self.xformer is not None:
            self.xformer(tag)

        return self.stop_processing


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

       Milestone 3 also introduces a rule registry interface. You can create an
       empty :class:`SoupReplacer` and register multiple targeted rules::

           replacer = SoupReplacer()
           replacer.register_rule(tag_name="b", new_name="strong")
           replacer.register_rule(
               match=lambda tag: tag.has_attr("data-upgrade"),
               attrs_xformer=lambda tag: {**tag.attrs, "data-upgraded": "yes"},
           )

       The helper :meth:`from_rules` constructor accepts declarative rule
       dictionaries for the same effect.
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
            rules: Optional[Iterable[Mapping[str, Any]]] = None,
    ) -> None:
        self._rules: list[_ReplacementRule] = []
        self._simple_map: dict[str, str] = {}

        simple_mode = og_tag is not None or alt_tag is not None

        if simple_mode:
            if any((name_xformer, attrs_xformer, xformer)) or rules:
                raise ValueError(
                    "Positional tag replacement arguments cannot be combined "
                    "with transformer callables or rule configurations."
                )
            if not og_tag or not alt_tag:
                raise ValueError("og_tag and alt_tag must be non-empty")
            self._og = og_tag.lower()
            self._alt = alt_tag.lower()
            self._name_xformer = None
            self._attrs_xformer = None
            self._xformer = None
            self._register_simple_rule(self._og, self._alt)
            return

        self._og = None
        self._alt = None
        self._name_xformer = name_xformer
        self._attrs_xformer = attrs_xformer
        self._xformer = xformer

        if any((name_xformer, attrs_xformer, xformer)):
            self._add_rule(
                match=_match_any,
                name_xformer=name_xformer,
                attrs_xformer=attrs_xformer,
                xformer=xformer,
            )

        if rules:
            for spec in rules:
                self.register_rule(**spec)

    # ------------------------------------------------------------------
    # Compatibility helpers for the milestone-2 API
    # ------------------------------------------------------------------
    def preprocess_name(self, name: str) -> str:
        """Return the tag name that should be used when creating a tag."""

        if not name:
            return name

        lowered = name.lower()

        mapped = self._simple_map.get(lowered)
        if mapped is not None:
            return mapped

        if self._og is not None and lowered == self._og:
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

        for rule in self._rules:
            try:
                stop = rule.apply(tag)
            except Exception:
                continue
            if stop:
                break

    # ------------------------------------------------------------------
    # Rule registration API
    # ------------------------------------------------------------------
    def _add_rule(
            self,
            *,
            match: MatchPredicate,
            name_xformer: Optional[NameTransformer] = None,
            attrs_xformer: Optional[AttrsTransformer] = None,
            xformer: Optional[TagTransformer] = None,
            priority: int = 0,
            stop_processing: bool = False,
    ) -> _ReplacementRule:
        rule = _ReplacementRule(
            match=match,
            name_xformer=name_xformer,
            attrs_xformer=attrs_xformer,
            xformer=xformer,
            priority=priority,
            stop_processing=stop_processing,
        )
        self._rules.append(rule)
        self._rules.sort(key=lambda r: r.priority, reverse=True)
        return rule

    def _register_simple_rule(self, og_name: str, alt_name: str) -> None:
        self._simple_map[og_name] = alt_name

        def match(tag: "Tag", og=og_name) -> bool:
            return bool(tag.name) and tag.name.lower() == og

        def rename(_: "Tag", alt=alt_name) -> str:
            return alt

        self._add_rule(match=match, name_xformer=rename)

    def register_rule(
            self,
            *,
            tag_name: Optional[str] = None,
            match: Optional[MatchPredicate] = None,
            new_name: Optional[str] = None,
            name_xformer: Optional[NameTransformer] = None,
            new_attrs: Optional[Mapping[str, Any]] = None,
            attrs_xformer: Optional[AttrsTransformer] = None,
            xformer: Optional[TagTransformer] = None,
            priority: int = 0,
            stop_processing: bool = False,
    ) -> _ReplacementRule:
        """Register a new transformation rule.

        :param tag_name: Restrict the rule to tags with this name (case-insensitive).
        :param match: Optional predicate that decides whether a tag should be
            transformed. Mutually exclusive with ``tag_name``.
        :param new_name: Replace the tag name with this constant string.
        :param name_xformer: Callable that computes a replacement name.
        :param new_attrs: Replace the attribute mapping with this constant mapping.
        :param attrs_xformer: Callable that computes replacement attributes.
        :param xformer: Callable that can mutate the tag in place.
        :param priority: Higher priority rules run before lower priority rules.
        :param stop_processing: Stop evaluating further rules when this one runs.
        :return: The registered rule object.
        """

        if tag_name is not None and match is not None:
            raise ValueError("tag_name and match cannot both be provided")

        if tag_name is not None:
            lowered = tag_name.lower()

            def match_name(tag: "Tag", expected=lowered) -> bool:
                return bool(tag.name) and tag.name.lower() == expected

            match = match_name
        elif match is None:
            match = _match_any

        if new_name is not None and name_xformer is not None:
            raise ValueError("new_name and name_xformer are mutually exclusive")
        if new_attrs is not None and attrs_xformer is not None:
            raise ValueError("new_attrs and attrs_xformer are mutually exclusive")

        if new_name is not None:

            def constant_name(_: "Tag", value=new_name) -> str:
                return value

            name_xformer = constant_name

        if new_attrs is not None:

            def constant_attrs(_: "Tag", value=new_attrs) -> Mapping[str, Any]:
                return value

            attrs_xformer = constant_attrs

        if not any((name_xformer, attrs_xformer, xformer)):
            raise ValueError(
                "At least one transformation must be provided for a rule."
            )

        return self._add_rule(
            match=match,
            name_xformer=name_xformer,
            attrs_xformer=attrs_xformer,
            xformer=xformer,
            priority=priority,
            stop_processing=stop_processing,
        )

    @classmethod
    def from_rules(cls, *rules: Mapping[str, Any]) -> "SoupReplacer":
        """Create a :class:`SoupReplacer` from declarative rule dictionaries."""

        replacer = cls()
        for spec in rules:
            replacer.register_rule(**spec)
        return replacer

    @property
    def rules(self) -> tuple[_ReplacementRule, ...]:
        """Return a snapshot of the currently registered rules."""

        return tuple(self._rules)
