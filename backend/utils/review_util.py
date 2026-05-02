import json


def save_reviews(reviews: list[dict], path: str = "reviews.json"):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(reviews, f, ensure_ascii=False, indent=2)
    print(f"[fetcher] Saved to {path}")



def load_reviews(path: str = "idk.json") -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

