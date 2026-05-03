import chromadb
from chromadb import GetResult
from datetime import datetime, timezone, timedelta


chroma_client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = chroma_client.get_or_create_collection(name="place_reviews")


def generate_place_id(place_name: str, location: str) -> str:
    return f"{place_name.strip().lower().replace(' ', '_')}_{location.strip().lower().replace(' ', '_')}"

def is_valid_document(collection_result: GetResult, max_age_days: int) -> bool:
    if len(collection_result["documents"]) == 0:
        return False
    
    cached_at_string = collection_result["metadatas"][0]["cached_at"]
    was_cached_at = datetime.fromisoformat(cached_at_string)
    
    currect_datetime = datetime.now(timezone.utc)

    age = currect_datetime - was_cached_at

    if age > timedelta(days=max_age_days):
        return False
    
    return True

def store_summary(place_name: str, location: str, review_summary: str) -> None:
    place_id = generate_place_id(place_name, location)

    collection.upsert(
        documents=[review_summary],
        metadatas=[{
            "place_name": place_name,
            "location": location,
            "cached_at": datetime.now(timezone.utc).isoformat()
        }],
        ids=[place_id]
    )
    print("[VECTOR STORE] Summary stored")


def get_stored_summary(place_name: str, location: str, max_age_days: int = 30) -> str | None:
    place_id = generate_place_id(place_name, location)

    collection_result = collection.get(
        ids=[place_id],
        include=["documents", "metadatas"]
    )

    if not is_valid_document(collection_result, max_age_days):
        return None
    
    cached_review = collection_result["documents"][0]
    print("[VECTOR STORE] Got Stored Summary")
    return cached_review
    
