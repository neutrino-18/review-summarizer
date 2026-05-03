import json
import os

def save_reviews(place_name: str, location: str, reviews: list[dict]) -> None:
    filename = f"{place_name.strip().lower().replace(' ', '_')}_{location.strip().lower().replace(' ', '_')}_reviews.json"
    filepath = os.path.join("saved_reviews", filename)
    
    os.makedirs("saved_reviews", exist_ok=True)
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(reviews, f, ensure_ascii=False, indent=2)
    
    print(f"[UTILS] Reviews saved to {filepath}")


def load_reviews(place_name: str, location: str) -> list[dict] | None:
    filename = f"{place_name.strip().lower().replace(' ', '_')}_{location.strip().lower().replace(' ', '_')}_reviews.json"
    filepath = os.path.join("saved_reviews", filename)
    
    if not os.path.exists(filepath):
        return None
    
    with open(filepath, "r", encoding="utf-8") as f:
        reviews = json.load(f)
    
    print(f"[UTILS] Loaded reviews from {filepath}")
    return reviews