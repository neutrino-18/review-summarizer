from fastapi import APIRouter, HTTPException
from models.request_model import ReviewRequest
from models.response_model import ReviewResponse
from pipelines.graph.review_graph import graph

router = APIRouter()

@router.post("/summarize", response_model=ReviewResponse)
async def summarize(request: ReviewRequest):
    
    result = graph.invoke({
        "user_query": request.query,
        "no_info": False,
        "no_reviews": False,
    })

    if result["no_info"]:
        raise HTTPException(status_code=400, detail="Could not extract place name from query")
    
    if result["no_reviews"]:
        raise HTTPException(status_code=404, detail="No reviews found for this place")

    summary = result["summary"]

    return ReviewResponse(
        place_name=result["place_name"],
        location=result["location"],
        summary=summary["summary"],
        from_cache=result["from_cache"],
        thread_id=request.thread_id
    )