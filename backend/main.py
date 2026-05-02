from services.apify_service import fetch_reviews
from services.llm_service import summarize_reviews
from utils.review_util import save_reviews


PLACE_NAME = "Nithya Amirtham"
PLACE_LOCATION = "Adyar"
MAX_REVIEWS = 10

def main():
    reviews = fetch_reviews(
            place_name= PLACE_NAME,
            location= PLACE_LOCATION,
            max_reviews= MAX_REVIEWS,
        )

    save_reviews(reviews=reviews)

    updated_reviews = reviews[:MAX_REVIEWS]

    final_output : str = summarize_reviews(
            place_name = PLACE_NAME,
            place_location = PLACE_LOCATION,
            reviews = updated_reviews
        )

    print(f"[Main] Gemini gave this output: {final_output}")

if __name__ == "__main__":
    main()