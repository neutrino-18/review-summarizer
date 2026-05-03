from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from core.config import GEMINI_TOKEN
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GEMINI_TOKEN,
    temperature=0.1
)

def format_reviews_for_prompt(reviews: list[dict]) -> str:
    formatted_str = ""
    for review_cnt, review in enumerate(reviews, start=1):

        author = review.get('author')
        rating = review.get('rating')
        text = review.get('text')

        formatted_str += (f'{review_cnt}. {author} says "{text}" and gave a rating of {rating}\n')

    print(f"[REVIEW PIPELINE] Final review string for prompt prepared.")
    return formatted_str

# extracting place name and location from the user query.
def extract_place_info(user_query: str) -> dict:
    prompt = PromptTemplate(
        input_variables=["user_query"],
        template= """
        You are a information extraction system

        Task:
        Extract a single place or business name and its location from the user query.

        Rules:
        - Return ONLY a valid JSON object. No explanation, no extra text, no formatting, just the JSON.
        - JSON keys MUST be exactly 'place_name', 'location'.
        - If multiple places/businesses or locations are mentioned, return the most relevant one.
        - If no place name is found, set 'place_name' to "".
        - If no location is found, set 'location' to "".
        - Keep values concise and clean (no extra words like "near", "around", "in", etc.).
        - Do not infer missing information beyond what is explicitly stated.

        Examples:
        Input: "Reviews about Starbucks in New York"
        Output: {{ "place_name": "Starbucks", "location": "New York" }}

        Input: "How's the vibe at Nithya Amirtham?"
        Output: {{ "place_name": "Nithya Amirtham", "location": "" }}

        Input: "Find me the best pizza place nearby"
        Output: {{ "place_name": "", "location": "" }}

        Now extract the information from this query: 
        {user_query}
        """
    )
    print("[REVIEW PIPELINE] extraction prompt ready")


    chain = prompt | llm | JsonOutputParser()
    print("[REVIEW PIPELINE] extraction chain ready")


    place_info: dict = chain.invoke({"user_query" : user_query})
    print("[REVIEW PIPELINE] extraction chain invoked")


    print(f"[REVIEW PIPELINE] Place info ready: {place_info}")
    return place_info


def summarize_reviews(place_name: str, location: str, reviews: list[dict]) -> dict:
    reviews = format_reviews_for_prompt(reviews)

    prompt = PromptTemplate(
        input_variables=["place_name", "location", "reviews"],
        template="""
        You are a professional summarizer

        Task:
        Summarize attached reviews into lists of pros and cons separtely for this place: {place_name} which is located here: {location}.

        Rules:
        - Return ONLY a valid JSON object. No explanation, no extra text, no formatting, just the JSON.
        - JSON keys MUST be exactly 'pros', 'cons'.
        - JSON values MUST be a list of complete summarized sentences based on all the reviews, not just the keywords.
        - Combine related points from multiple reviews into single coherent sentences.
        - Be decriptive about explaning using joining words, expressions etc.
        - Each point should be a full sentence that would make sense on its own.
        - Do not infer missing information beyond what is explicitly stated.

        STRICT RULE:
        If a fact is not explicitly mentioned in the reviews below, do NOT include it.
        Treat this as if you have no prior knowledge of this place and just blindly refer the given reviews.

        Example Output:
        {{"pros": ["It is very good place", 'Its food is very tasty'], "cons": ["Hygiene is not maintained"]}}

        Now summarize these reviews accordingly:
        {reviews}
        """
    )
    print("[REVIEW PIPELINE] summarize prompt ready")

    
    chain = prompt | llm | JsonOutputParser()
    print("[REVIEW PIPELINE] summarize chain ready")


    final_pros_cons: dict = chain.invoke({"place_name": place_name, "location" : location, "reviews": reviews})
    print("[REVIEW PIPELINE] summarize chain invoked")


    print(f"[REVIEW PIPELINE] Final Pros and Cons are: {final_pros_cons}")
    return final_pros_cons