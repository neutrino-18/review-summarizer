from typing import TypedDict

class ReviewState(TypedDict):
    user_query: str
    place_name: str
    location: str
    reviews: list
    summary: dict
    from_cache: bool
    no_reviews: bool
    no_info: bool