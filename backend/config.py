import requests
from dotenv import load_dotenv
import os


load_dotenv()

APIFY_TOKEN = os.getenv('APIFY_REVEIW_SCRAPER_API')

APIFY_ACTOR_URL = (
    "https://api.apify.com/v2/acts/compass~google-maps-reviews-scraper"
    "/run-sync-get-dataset-items"
    f"?token={APIFY_TOKEN}"
)