from pydantic import BaseModel

class ReviewRequest(BaseModel):
    query: str
    thread_id: str