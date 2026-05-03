from dotenv import load_dotenv
import os


load_dotenv()

APIFY_TOKEN = os.getenv('APIFY_REVEIW_SCRAPER_API')
GEMINI_TOKEN = os.getenv('GEMINI_API')