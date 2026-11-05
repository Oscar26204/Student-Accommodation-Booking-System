"""Search and filter listings (backlog item 4)."""
from __future__ import annotations

from dataclasses import dataclass

from .errors import ValidationError
from .listings import Listing, RoomType

NO_MATCH_MESSAGE = "No listings match your filters. Try widening your budget or distance."


@dataclass(frozen=True)
class SearchCriteria:
    min_rent: int | None = None
    max_rent: int | None = None
    room_type: RoomType | None = None
    max_distance_km: float | None = None


@dataclass(frozen=True)
class SearchResult:
    items: list[Listing]
    message: str = ""

    def cards(self) -> list[dict]:
        return [item.to_card() for item in self.items]


def _validate(criteria: SearchCriteria) -> None:
    for label, value in (
        ("minimum rent", criteria.min_rent),
        ("maximum rent", criteria.max_rent),
        ("maximum distance", criteria.max_distance_km),
    ):
        if value is not None and value < 0:
            raise ValidationError(f"The {label} cannot be negative.")
    if (
        criteria.min_rent is not None
        and criteria.max_rent is not None
        and criteria.min_rent > criteria.max_rent
    ):
        raise ValidationError("Minimum rent cannot be higher than maximum rent.")


def _matches(listing: Listing, c: SearchCriteria) -> bool:
    if not listing.available:
        return False
    if c.min_rent is not None and listing.rent < c.min_rent:
        return False
    if c.max_rent is not None and listing.rent > c.max_rent:
        return False
    if c.room_type is not None and listing.room_type is not c.room_type:
        return False
    if c.max_distance_km is not None and listing.distance_to_campus_km > c.max_distance_km:
        return False
    return True


def search_listings(listings: list[Listing], criteria: SearchCriteria | None = None) -> SearchResult:
    """Return matching, available listings (cheapest first, then nearest)."""
    criteria = criteria or SearchCriteria()
    _validate(criteria)
    matches = sorted(
        (l for l in listings if _matches(l, criteria)),
        key=lambda l: (l.rent, l.distance_to_campus_km),
    )
    if not matches:
        return SearchResult(items=[], message=NO_MATCH_MESSAGE)
    return SearchResult(items=matches)
