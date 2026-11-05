"""Add property listing (backlog item 3)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .auth import Role, User
from .errors import PermissionDenied, ValidationError
from .storage import Repository


class RoomType(str, Enum):
    SINGLE = "single"
    BEDSITTER = "bedsitter"
    ONE_BEDROOM = "one_bedroom"
    SHARED = "shared"


@dataclass(frozen=True)
class Listing:
    listing_id: int
    landlord_id: int
    name: str
    location: str
    rent: int  # Kenya shillings per month
    room_type: RoomType
    description: str
    photos: tuple[str, ...]
    distance_to_campus_km: float
    available: bool = True

    def to_card(self) -> dict:
        """What a student sees in search results.

        Privacy: landlord phone/email are deliberately NOT included here.
        """
        return {
            "listing_id": self.listing_id,
            "name": self.name,
            "photo": self.photos[0],
            "rent": self.rent,
            "location": self.location,
            "distance_to_campus_km": self.distance_to_campus_km,
        }


class ListingService:
    def __init__(self, repo: Repository) -> None:
        self._repo = repo

    def add_listing(
        self,
        landlord: User,
        *,
        name: str,
        location: str,
        rent,
        room_type,
        description: str,
        photos: list[str] | None,
        distance_to_campus_km,
    ) -> Listing:
        if landlord.role is not Role.LANDLORD:
            raise PermissionDenied("Only landlords can add listings.")

        missing = []
        if not (name or "").strip():
            missing.append("name")
        if not (location or "").strip():
            missing.append("location")
        if rent in (None, ""):
            missing.append("rent")
        if room_type in (None, ""):
            missing.append("room type")
        if not (description or "").strip():
            missing.append("description")
        if not photos:
            missing.append("at least one photo")
        if distance_to_campus_km in (None, ""):
            missing.append("distance to campus")
        if missing:
            raise ValidationError("Missing required field(s): " + ", ".join(missing))

        try:
            rent_value = int(rent)
            distance_value = float(distance_to_campus_km)
            room = RoomType(room_type)
        except (TypeError, ValueError):
            raise ValidationError("Rent, distance or room type is not valid.") from None
        if rent_value <= 0:
            raise ValidationError("Rent must be greater than zero.")
        if distance_value < 0:
            raise ValidationError("Distance to campus cannot be negative.")

        listing = Listing(
            listing_id=self._repo.next_listing_id(),
            landlord_id=landlord.user_id,
            name=name.strip(),
            location=location.strip(),
            rent=rent_value,
            room_type=room,
            description=description.strip(),
            photos=tuple(photos),
            distance_to_campus_km=distance_value,
        )
        self._repo.listings[listing.listing_id] = listing
        return listing

    def list_for_landlord(self, landlord_id: int) -> list[Listing]:
        return [l for l in self._repo.listings.values() if l.landlord_id == landlord_id]

    def all_listings(self) -> list[Listing]:
        return list(self._repo.listings.values())
