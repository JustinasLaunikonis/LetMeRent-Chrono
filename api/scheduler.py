from apscheduler.schedulers.background import BackgroundScheduler

from api.config import SCHEDULER_INTERVAL_MINUTES
from api.scraper_client import ScraperClient


class ChronoScheduler:
    def __init__(self):
        # Create a background scheduler
        self.scheduler = BackgroundScheduler()

        # Create scraper API client
        self.client = ScraperClient()

    def start(self):
        # Add a scheduled job that runs every configured number of minutes
        self.scheduler.add_job(
            self.run_tasks,
            "interval",
            minutes=SCHEDULER_INTERVAL_MINUTES,
            id="chrono_tasks",
            replace_existing=True
        )

        # Start the scheduler
        self.scheduler.start()

        print("Chrono scheduler started.")

    def run_tasks(self):
        # Log task start
        print("Running scheduled chrono tasks...")

        # Run spiders through scraper API
        spiders_result = self.client.run_spiders()

        # Print spiders execution result
        print("Spiders result:", spiders_result)

        # Delete old listings
        delete_result = self.client.delete_old_listings()

        # Print delete result
        print("Delete old listings result:", delete_result)

        # Log task completion
        print("Scheduled chrono tasks finished.")