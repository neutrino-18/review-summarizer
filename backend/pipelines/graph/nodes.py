from pipelines.graph.state import ReviewState
from pipelines.review_pipeline import summarize_reviews, extract_place_info, detect_intent, rewrite_on_intent, normal_conversation
from services.apify_service import fetch_reviews
from utils.review_util import save_reviews, load_reviews
from rag.vector_store import store_summary, get_stored_summary
from rag.retriever import store_reviews_for_retrieval, retrieve_relevant_reviews
from core.config import MAX_AGE_DAYS, MAX_REVIEWS


# Node: Extract place info node
def extract_place_node(state: ReviewState) -> dict:
    place_info: dict = extract_place_info(state["user_query"])

    place_name: str = place_info["place_name"].lower()
    location: str = place_info["location"].lower()

    print(f"[GRAPH] Extracted {place_name} and {location} from user query")

    if not place_name:
        print("[GRAPH] No place name found. Routing to intent detection")
        return {"is_follow_up" : True}
    
    print(f"[GRAPH] Place name identified")
    return {"place_name": place_name, "location": location, "is_follow_up": False}


# Conditional Edge: if info extracted or not
def route_after_extract(state: ReviewState)-> str:
    if state["is_follow_up"]:
        return "detect_intent"
    
    return "check_cache"



def detect_intent_node(state: ReviewState) -> dict:
    history = state.get("conversation_history", "")

    intent = detect_intent(state["user_query"], history)

    if intent == "contextless":
        print("[GRAPH] Conversational intent")
        return {"is_normal_convo": True}
    
    print(f"[GRAPH] Detected intent: {intent}")
    return {"intent": intent, "is_normal_convo": False}


def route_after_intent(state: ReviewState)-> str:
    if state["is_normal_convo"]:
        return "normal_conversation"
    
    return "rewrite_on_intent"




def normal_conversation_node(state: ReviewState) -> dict:
    response = normal_conversation(state["user_query"])
    print("[GRAPH] Normally responed based on contextless query")

    history = state.get("conversation_history", "")
    updated_history = f"{history}\nUser: {state['user_query']}\nAI: {response}".strip()
    return {"summary": response, "conversation_history": updated_history}



def rewrite_on_intent_node(state: ReviewState) -> dict:
    relevant_reviews = retrieve_relevant_reviews(
        intent=state["intent"],
        place_name=state["place_name"]
    )
    history = state.get("conversation_history", "")
    response = rewrite_on_intent(
        place_name=state["place_name"],
        intent=state["intent"],
        relevant_reviews=relevant_reviews,
        conversation_history=history
    )
    print("[GRAPH] Rewrote response based on intent")
    updated_history = f"{history}\nUser: {state['user_query']}\nAI: {response}".strip()
    return {"summary": response, "conversation_history": updated_history}


# Node: Check vector cache for summary
def check_cache_node(state: ReviewState) -> dict:
    cached = get_stored_summary(
        place_name=state["place_name"],
        location=state["location"],
        max_age_days=MAX_AGE_DAYS
    )
    if cached:
        print("[GRAPH] Cache Hit.")
        return {"summary": cached, "from_cache": True}
    
    print("[GRAPH] Cache Miss.")
    return {"from_cache": False}

# Conditional Edge: if cache hit or miss
def route_after_cache(state: ReviewState) -> str:
    if state["from_cache"]:
        return "end"
    
    return "load_reviews"



# Node: Load reviews from either local storage or apify
def load_reviews_node(state: ReviewState) -> dict:
    
    print("[GRAPH] Checking for saved reviews")
    reviews = load_reviews(state["place_name"], state["location"])
    fresh = False
    if reviews is None:
        print("[GRAPH] No saved reviews. Fetching from Apify.")

        reviews = fetch_reviews(state["place_name"], state["location"], MAX_REVIEWS)

        if not reviews:
            print("[GRAPH] No reviews found from Apify.")
            summary = "No listed reviews found for the specific query"
            return {"reviews": [], "no_reviews": True, "summary": summary}
        
        # saving reviews to local storage here btw
        save_reviews(state["place_name"], state["location"], reviews)
        fresh = True

    updated_reviews = reviews
    if fresh:
        store_reviews_for_retrieval(state["place_name"], state["location"], updated_reviews)

    return {"reviews": updated_reviews, "no_reviews": False}

# Conditional Edge: if reviews present or not
def route_after_load(state: ReviewState) -> str:  
    if state["no_reviews"]:
        return "end"
    return "summarize"



# Node: Summarize the reviews
def summarize_node(state: ReviewState) -> dict:
    print("[GRAPH] Way to summarization")
    
    summary = summarize_reviews(state["place_name"], state["location"], state["reviews"])
    print("[GRAPH] Summarized the Reviews.")

    history = state.get("conversation_history", "")
    updated_history = f"{history}\nUser: {state['user_query']}\nAI: {summary}".strip()

    return {"summary" : summary, "conversation_history": updated_history}



# Node: Store the reviews in cache
def store_summary_node(state: ReviewState) -> dict:

    store_summary(state["place_name"], state["location"], state["summary"])
    print("[GRAPH] Stored into Cache.") 

    return {}