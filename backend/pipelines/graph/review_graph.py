from langgraph.graph import StateGraph, END
from pipelines.graph.state import ReviewState
from pipelines.review_pipeline import summarize_reviews, extract_place_info
from services.apify_service import fetch_reviews
from utils.review_util import save_reviews, load_reviews
from rag.vector_store import store_summary, get_stored_summary
from core.config import MAX_AGE_DAYS, MAX_REVIEWS

# Node: Extract place info node
def extract_place_node(state: ReviewState) -> dict:
    place_info: dict = extract_place_info(state["user_query"])

    place_name: str = place_info["place_name"]
    location: str = place_info["location"]
    print(f"[GRAPH] Extracted {place_name} and {location} from user query")

    if len(place_name) == 0:

        print("[GRAPH] empty name and location. So exiting")
        return {"no_info" : True}
    
    return {"place_name": place_name, "location": location}

# Conditional Edge: if info extracted or not
def route_after_extract(state: ReviewState)-> str:
    if state["no_info"]:
        return "end"
    
    return "check_cache"



# Node: Check vector cache for reviews
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

    if reviews is None:
        print("[GRAPH] No saved reviews. Fetching from Apify.")

        reviews = fetch_reviews(state["place_name"], state["location"], MAX_REVIEWS)

        if not reviews:
            print("[GRAPH] No reviews found from Apify.")
            return {"reviews": [], "no_reviews": True}
        
        # saving reviews to local storage here btw
        save_reviews(state["place_name"], state["location"], reviews)

    updated_reviews = reviews[:MAX_REVIEWS]
    return {"reviews": updated_reviews}

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

    return {"summary" : summary}



# Node: Store the reviews in cache
def store_summary_node(state: ReviewState) -> dict:

    store_summary(state["place_name"], state["location"], state["summary"])
    print("[GRAPH] Stored into Cache.")

    return {}


builder = StateGraph(ReviewState)

builder.add_node("extract_place", extract_place_node)
builder.add_node("check_cache", check_cache_node)
builder.add_node("load_reviews", load_reviews_node)
builder.add_node("summarize", summarize_node)
builder.add_node("store_summary", store_summary_node)

builder.set_entry_point("extract_place")


builder.add_conditional_edges(
    "extract_place",
    route_after_extract,
    {
        "end": END,
        "check_cache": "check_cache"
    }
)

builder.add_conditional_edges(
    "check_cache",
    route_after_cache,
    {
        "end": END,
        "load_reviews": "load_reviews"
    }
)

builder.add_conditional_edges(
    "load_reviews", 
    route_after_load,
    {
        "end": END,
        "summarize": "summarize"
    }
)

builder.add_edge("summarize", "store_summary")
builder.add_edge("store_summary", END)


graph = builder.compile()