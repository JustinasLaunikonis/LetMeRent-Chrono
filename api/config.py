import os

SCRAPER_SERVICE_URL = os.getenv("SCRAPER_SERVICE_URL", "http://localhost:5000")
OLD_LISTINGS_DAYS = int(os.getenv("OLD_LISTINGS_DAYS", "30"))
SCHEDULER_INTERVAL_MINUTES = int(os.getenv("SCHEDULER_INTERVAL_MINUTES", "10"))

MAIL_SERVER = os.getenv("SMTP_HOST", "smtp.gmail.com")
MAIL_PORT = int(os.getenv("SMTP_PORT", "587"))
MAIL_USERNAME = os.getenv("SMTP_USER")
MAIL_PASSWORD = os.getenv("SMTP_PASSWORD")
MAIL_USE_TLS = True
MAIL_USE_SSL = False

EMAIL_FROM = os.getenv("EMAIL_FROM", MAIL_USERNAME)