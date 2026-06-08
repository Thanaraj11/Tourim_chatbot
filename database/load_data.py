from .db import Database

def fetch_all_tourism_data():
    db = Database()
    try:
        data = {
            "places": db.get_all_places(),
            "hotels": db.get_all_hotels(),
            "restaurants": db.get_all_restaurants(),
            "guides": db.get_all_guides(),
            "packages": db.get_all_packages()
        }
        return data
    finally:
        db.close()