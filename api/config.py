import os
from dotenv import load_dotenv

load_dotenv()

SCRAPER_SERVICE_URL = os.getenv("SCRAPER_SERVICE_URL", "http://localhost:5000")
OLD_LISTINGS_DAYS = int(os.getenv("OLD_LISTINGS_DAYS", "30"))
SCHEDULER_INTERVAL_MINUTES = int(os.getenv("SCHEDULER_INTERVAL_MINUTES", "10"))