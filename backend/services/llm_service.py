from google import genai
from core.config import GEMINI_TOKEN

gemini_client = genai.Client(api_key=GEMINI_TOKEN)
GEMINI_MODEL = 'gemini-2.5-flash'


def format_reviews_for_prompt(reviews: list[dict]) -> str:
    formatted_str = ""
    for review_cnt, review in enumerate(reviews, start=1):

        author = review.get('author')
        rating = review.get('rating')
        text = review.get('text')

        formatted_str += (f'{review_cnt}. {author} says "{text}" and gave a rating of {rating}\n')

    print(f"[LLM SERVICE] Final review string for prompt prepared.")
    return formatted_str


def summarize_reviews(place_name: str, place_location: str, reviews: list[dict]) -> str:

    formatted_reviews = format_reviews_for_prompt(reviews)

    prompt = f"""
        [ROLE]: You are a professional summarizer who ONLY summarizes from what is given and not from your own memory.
        [STRICT RULE]: If a fact is not explicitly mentioned in the reviews above, do NOT include it.
        Treat this as if you have no prior knowledge of this place and just blindly refer the given reviews.
        [CONTEXT]: I am giving you some reviews for: {place_name} which is situated in {place_location}.
        [TASK]: Your task is to summarize these reviews into a combined list of pros and cons in a defined format mentioned hereinafter.
        [REVIEWS]:
        {formatted_reviews}
        [OUTPUT]: The output should be a bulleted list of at max 5 pros and then different bulleted list of at max 5 cons for the reviews.
        If there are not enough points for 5 pros and cons, just give how many there is possible, no need for 5.
    """
    
    print(f"[LLM SERVICE] Prompt Ready. Onto Cooking")
    response = gemini_client.models.generate_content(
        model = GEMINI_MODEL,
        contents = prompt
    )
    print("[LLM SERVICE] Generative Gemini cooked")
    return response.text