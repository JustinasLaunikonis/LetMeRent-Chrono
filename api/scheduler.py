from apscheduler.schedulers.background import BackgroundScheduler

from api.config import SCHEDULER_INTERVAL_MINUTES
from api.scraper_client import ScraperClient


class ChronoScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.client = ScraperClient()

    def start(self):
        self.scheduler.add_job(
            self.run_tasks,
            "interval",
            minutes=SCHEDULER_INTERVAL_MINUTES,
            id="chrono_tasks",
            replace_existing=True
        )

        self.scheduler.start()
        print("Chrono scheduler started.")

    def run_tasks(self):
        print("Running scheduled chrono tasks...")

        spiders_result = self.client.run_spiders()
        print("Spiders result:", spiders_result)

        delete_result = self.client.delete_old_listings()
        print("Delete old listings result:", delete_result)

        print("Scheduled chrono tasks finished.")