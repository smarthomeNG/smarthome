#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""Test stand-in for the database plugin's per-item data-gap functions."""

from lib.item.item import Item


class GapRecorder:
    """
    Replaces an item's ``db_mark_invalid``/``db_is_invalid``, which the database plugin injects
    into every item it logs.

    Follows their contract: marking opens a gap and records the call; the gap stays open
    until the test resets ``open_gap``.
    """

    def __init__(self, item: Item) -> None:
        self.calls: list[tuple[str | None, str | None]] = []
        self.open_gap = False
        item.db_mark_invalid = self.mark_invalid
        item.db_is_invalid = self.is_invalid

    def mark_invalid(self, caller: str | None = None, source: str | None = None) -> None:
        self.calls.append((caller, source))
        self.open_gap = True

    def is_invalid(self) -> bool:
        return self.open_gap
