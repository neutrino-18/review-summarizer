from dotenv import load_dotenv
import os


load_dotenv()

APIFY_TOKEN = os.getenv('APIFY_REVEIW_SCRAPER_API')
GEMINI_TOKEN = os.getenv('GEMINI_API')
OPEN_AI_API = os.getenv('OPEN_AI_API')
MAX_REVIEWS = 20
MAX_AGE_DAYS = 30