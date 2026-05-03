from pipelines.review_pipeline import summarize_reviews, extract_place_info
from services.apify_service import fetch_reviews
from utils.review_util import save_reviews, load_reviews
from rag.vector_store import store_summary, get_stored_summary

USERQUERY = "What are the reviews of Starbucks in Udaipur?"
MAX_REVIEWS = 20
MAX_AGE_DAYS = 30


def main():
    place_info = extract_place_info(USERQUERY)

    place_name = place_info["place_name"]
    location = place_info["location"]

    print(f"[MAIN] Extracted {place_name} and {location} from user query")

    cached = get_stored_summary(
        place_name=place_name,
        location=location,
        max_age_days=MAX_AGE_DAYS
    )

    if cached:
        print("[MAIN] Cache Hit.")
        print(cached)
        return
    
    print("[MAIN] Cache Miss")

    reviews = load_reviews(place_name, location)

    if reviews is None:
        print("[MAIN] No saved reviews. Fetching from Apify.")

        reviews = fetch_reviews(place_name, location, MAX_REVIEWS)
        save_reviews(place_name, location, reviews)

    if not reviews:
        print("[MAIN] No reviews Found!")
        return

    updated_reviews = reviews[:MAX_REVIEWS]


    final_summary : dict = summarize_reviews(place_name, location, updated_reviews)
    print(f"[Main] Gemini cooked this output: {final_summary}")
    store_summary(place_name, location, final_summary)

if __name__ == "__main__":
    main()