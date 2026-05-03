import requests
from backend.core.config import APIFY_TOKEN
from enum import Enum

class SortBy(Enum):
    MOSTRELEVANT = "mostRelevant"
    NEWEST = "newest"
    HIGHESTRANKING = "highestRanking"
    LOWESTRANKING = "lowestRanking"

APIFY_ACTOR_URL = (
    "https://api.apify.com/v2/acts/compass~google-maps-reviews-scraper"
    "/run-sync-get-dataset-items"
    f"?token={APIFY_TOKEN}"
)

def build_google_maps_url(business_name: str, location: str) -> str:
    query = f"{business_name} {location}".strip().replace(" ", "+")
    url = f"https://www.google.com/maps/search/{query}"
    print(f"[APIFY SERVICE] Maps URL: {url}")
    return url



def fetch_reviews(
    place_name: str,
    location: str,
    max_reviews: int = 5,          
    sort_by: SortBy = SortBy.MOSTRELEVANT,
) -> list[dict]:
    
    maps_url = build_google_maps_url(place_name, location)

    payload = {
        "startUrls": [
            {"url" : maps_url}
        ],
        "maxReviews": max_reviews,
        "reviewsSort": sort_by.value,
        "language": "en",
    }

    print(f"[APIFY SERVICE] Calling Apify... (this may take a min)")

    response = requests.post(
        APIFY_ACTOR_URL,
        json=payload,
        timeout=120,
    )

    if response.status_code != 200:
        print(f"[APIFY SERVICE] Error {response.status_code}: {response.text}")
        response.raise_for_status()


    raw_data = response.json()
    print(f"[APIFY SERVICE] Got {len(raw_data)} raw items from Apify")


    cleaned_reviews = []
    for item in raw_data:
        text = item.get("text", "") or ""
        text = text.strip()

        if not text:
            continue

        cleaned_reviews.append({
            "author":   item.get("name", "Anonymous"),
            "rating":   item.get("stars") or item.get("rating"),
            "text":     text,
            "likes":    item.get("likesCount", 0),
            "source":   "google_maps",
        })

    print(f"[APIFY SERVICE] Cleaned reviews: {len(cleaned_reviews)}")
    return cleaned_reviews
