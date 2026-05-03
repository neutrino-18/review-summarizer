from typing import TypedDict

class ReviewState(TypedDict):
    user_query: str
    place_name: str
    location: str
    reviews: list
    summary: str
    from_cache: bool
    no_reviews: bool
    is_follow_up: bool
    is_normal_convo: bool
    intent: str
    conversation_history: str