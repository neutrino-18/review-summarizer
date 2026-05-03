from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from pipelines.graph.nodes import extract_place_node, detect_intent_node, summarize_node, check_cache_node, load_reviews_node, store_summary_node, rewrite_on_intent_node, normal_conversation_node
from pipelines.graph.nodes import route_after_extract, route_after_cache, route_after_intent, route_after_load
from pipelines.graph.state import ReviewState


builder = StateGraph(ReviewState)

builder.add_node("extract_place", extract_place_node)
builder.add_node("detect_intent", detect_intent_node)
builder.add_node("rewrite_on_intent", rewrite_on_intent_node)
builder.add_node("check_cache", check_cache_node)
builder.add_node("load_reviews", load_reviews_node)
builder.add_node("summarize", summarize_node)
builder.add_node("store_summary", store_summary_node)
builder.add_node("normal_conversation", normal_conversation_node)


builder.set_entry_point("extract_place")

builder.add_conditional_edges(
    "extract_place",
    route_after_extract,
    {
        "detect_intent": "detect_intent",
        "check_cache": "check_cache"
    }
)

builder.add_conditional_edges(
    "detect_intent",
    route_after_intent,
    {
        "normal_conversation": "normal_conversation",
        "rewrite_on_intent": "rewrite_on_intent"
    }
)

builder.add_edge("rewrite_on_intent", END)
builder.add_edge("normal_conversation", END)

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

memory = MemorySaver()
graph = builder.compile(checkpointer=memory)