from fastapi import APIRouter, HTTPException
from models.request_model import ReviewRequest
from models.response_model import ReviewResponse
from pipelines.graph.graph import graph

router = APIRouter()

@router.post("/summarize", response_model=ReviewResponse)
async def summarize(request: ReviewRequest):
    
    config = {"configurable": {"thread_id": request.thread_id}}
    result = graph.invoke({
        "user_query": request.query,
        "no_reviews": False,
        "is_follow_up": False,
        "is_normal_convo": False
    }, config=config)
    
    if result["no_reviews"]:
        raise HTTPException(status_code=404, detail="No reviews found for this place")

    
    return ReviewResponse(
        place_name=result.get("place_name", ""),
        location=result.get("location", ""),
        summary=result.get("summary", ""),
        from_cache=result.get("from_cache", False),
        thread_id=request.thread_id
    )