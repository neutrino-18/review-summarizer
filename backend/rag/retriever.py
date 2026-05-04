from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vector_store = Chroma(
    collection_name="individual_reviews",
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)

def store_reviews_for_retrieval(place_name: str, location: str, reviews: list[dict]) -> None:
    texts = []
    metadata = []

    for review in reviews:
        if not review.get("text"):
            continue
        texts.append(review["text"])
        metadata.append({
            "place_name": place_name,
            "location": location,
            "author": review.get("author", "Anonymous"),
            "rating": str(review.get("rating", "")),
        })
    if texts:
        vector_store.add_texts(texts=texts, metadatas=metadata)


def retrieve_relevant_reviews(intent: str, place_name: str, k: int = 8) -> list[str]:
    retriever = vector_store.as_retriever(
        search_kwargs = {
            "k" : k,
            "filter" : {"place_name" : place_name}
        }
    )

    docs = retriever.invoke(intent)
    reviews = [doc.page_content for doc in docs]

    print(f"[RETRIEVER] Retrieved {len(reviews)} relevant reviews for intent: {intent}")

    return reviews