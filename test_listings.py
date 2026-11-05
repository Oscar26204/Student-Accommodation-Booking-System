"""Backlog item 3: add property listing (acceptance criteria from the SABS plan)."""
import pytest

from sabs.errors import PermissionDenied, ValidationError


def test_landlord_can_add_listing_with_photo(listings, landlord, valid_listing_data):
    listing = listings.add_listing(landlord, **valid_listing_data)
    assert listing.landlord_id == landlord.user_id
    assert listing.photos == ("front.jpg",)
    assert listing.available is True


def test_saved_listing_appears_in_landlords_property_list(listings, landlord, valid_listing_data):
    saved = listings.add_listing(landlord, **valid_listing_data)
    assert listings.list_for_landlord(landlord.user_id) == [saved]


def test_other_landlords_listings_are_not_shown(auth, listings, landlord, valid_listing_data):
    listings.add_listing(landlord, **valid_listing_data)
    other = auth.register_landlord("Peter", "peter@example.com", "Rooms2026", "0722222222")
    assert listings.list_for_landlord(other.user_id) == []


@pytest.mark.parametrize(
    "field, bad_value",
    [
        ("name", ""), ("location", "  "), ("rent", None),
        ("room_type", ""), ("description", ""), ("photos", []),
        ("distance_to_campus_km", None),
    ],
)
def test_missing_required_field_is_rejected(listings, landlord, valid_listing_data, field, bad_value):
    valid_listing_data[field] = bad_value
    with pytest.raises(ValidationError):
        listings.add_listing(landlord, **valid_listing_data)
    assert listings.all_listings() == []  # nothing saved


def test_error_message_names_every_missing_field(listings, landlord, valid_listing_data):
    valid_listing_data.update(name="", photos=[])
    with pytest.raises(ValidationError) as err:
        listings.add_listing(landlord, **valid_listing_data)
    assert "name" in str(err.value) and "photo" in str(err.value)


@pytest.mark.parametrize("rent", [0, -500, "abc"])
def test_invalid_rent_rejected(listings, landlord, valid_listing_data, rent):
    valid_listing_data["rent"] = rent
    with pytest.raises(ValidationError):
        listings.add_listing(landlord, **valid_listing_data)


def test_negative_distance_rejected(listings, landlord, valid_listing_data):
    valid_listing_data["distance_to_campus_km"] = -1
    with pytest.raises(ValidationError):
        listings.add_listing(landlord, **valid_listing_data)


def test_unknown_room_type_rejected(listings, landlord, valid_listing_data):
    valid_listing_data["room_type"] = "castle"
    with pytest.raises(ValidationError):
        listings.add_listing(landlord, **valid_listing_data)


def test_student_cannot_add_listing(listings, student, valid_listing_data):
    with pytest.raises(PermissionDenied):
        listings.add_listing(student, **valid_listing_data)


def test_card_shows_photo_rent_and_location(listings, landlord, valid_listing_data):
    card = listings.add_listing(landlord, **valid_listing_data).to_card()
    assert card["photo"] == "front.jpg" and card["rent"] == 4500 and card["location"] == "Gatundu Road"
