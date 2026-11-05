"""Sprint Review demo: python -m sabs.demo  (run from the src/ folder)"""
from .auth import AuthService
from .listings import ListingService, RoomType
from .search import SearchCriteria, search_listings
from .storage import Repository

SAMPLE_LISTINGS = [
    ("Green View Hostel", "Gatundu Road", 4500, "single", 0.4),
    ("Sunrise Bedsitters", "Section 9", 6500, "bedsitter", 0.9),
    ("Campus Edge Apartments", "Ngoingwa", 9000, "one_bedroom", 1.8),
    ("Mwangaza Shared Rooms", "Kiandutu", 3000, "shared", 2.5),
    ("Acacia Court", "Makongeni", 7000, "bedsitter", 1.2),
]


def build_demo_data():
    repo = Repository()
    auth, listings = AuthService(repo), ListingService(repo)
    landlord = auth.register_landlord("Demo Landlord", "landlord@example.com", "Demo1234", "0712345678")
    for name, location, rent, room, km in SAMPLE_LISTINGS:
        listings.add_listing(
            landlord, name=name, location=location, rent=rent, room_type=room,
            description=f"{name} - sample listing", photos=["photo1.jpg"],
            distance_to_campus_km=km,
        )
    return repo, auth, listings


if __name__ == "__main__":
    repo, auth, listings = build_demo_data()
    auth.register_student("Demo Student", "student@example.com", "Study2026")
    print(f"Logged in as: {auth.login('student@example.com', 'Study2026').full_name}\n")
    criteria = SearchCriteria(max_rent=7000, room_type=RoomType.BEDSITTER, max_distance_km=1.5)
    result = search_listings(listings.all_listings(), criteria)
    print("Bedsitters up to KES 7,000 within 1.5 km:")
    for card in result.cards():
        print(f"  - {card['name']} | KES {card['rent']} | {card['location']}")
    print("\nNo-match case:", search_listings(listings.all_listings(), SearchCriteria(max_rent=100)).message)
