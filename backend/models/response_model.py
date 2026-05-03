from pydantic import BaseModel

class ReviewResponse(BaseModel):
    place_name: str
    location: str
    summary: str
    from_cache: bool
    thread_id: str