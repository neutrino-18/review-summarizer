from services.apify_service import fetch_reviews
from services.llm_service import summarize_reviews
from utils.review_util import save_reviews, load_reviews
from rag.vector_store import store_summary, get_stored_summary


PLACE_NAME = "Nithya Amirtham"
PLACE_LOCATION = "Adyar"
MAX_REVIEWS = 10
MAX_AGE_DAYS = 30
def main():
    

    cached = get_stored_summary(
        place_name=PLACE_NAME,
        location=PLACE_LOCATION,
        max_age_days=MAX_AGE_DAYS
    )

    if cached:
        print("[MAIN] Cache Hit.")
        print(cached)
        return
    
    print("[MAIN] Cache Miss")

    reviews = load_reviews(PLACE_NAME, PLACE_LOCATION)

    if reviews is None:
        print("[MAIN] No saved reviews. Fetching from Apify.")

        reviews = fetch_reviews(PLACE_NAME, PLACE_LOCATION, MAX_REVIEWS)
        save_reviews(PLACE_NAME, PLACE_LOCATION, reviews)

    if not reviews:
        print("[MAIN] No reviews Found!")
        return

    updated_reviews = reviews[:MAX_REVIEWS]


    final_summary : str = summarize_reviews(PLACE_NAME, PLACE_LOCATION, updated_reviews)
    store_summary(PLACE_NAME, PLACE_LOCATION, final_summary)
    print(f"[Main] Gemini cooked this output: {final_summary}")

if __name__ == "__main__":
    main()