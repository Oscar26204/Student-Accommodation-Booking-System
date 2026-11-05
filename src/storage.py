"""In-memory repository shared by all features.

Sprint 1 keeps storage deliberately simple (XP: simplicity). Replace with a
database in a later iteration; the services only depend on this small API.
"""
from __future__ import annotations

from itertools import count


class Repository:
    def __init__(self) -> None:
        self.users: dict[int, object] = {}
        self.listings: dict[int, object] = {}
        self._user_ids = count(1)
        self._listing_ids = count(1)

    def next_user_id(self) -> int:
        return next(self._user_ids)

    def next_listing_id(self) -> int:
        return next(self._listing_ids)
