from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

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
            replace_existing=True,
            max_instances=1
        )

        self.scheduler.start()
        print("Chrono scheduler started.")

    def run_tasks(self):
        print("Running scheduled chrono tasks...")

        tasks_result = self.client.get_chrono_tasks()
        print("Chrono tasks result:", tasks_result)

        if tasks_result["status_code"] != 200:
            print("Could not fetch chrono tasks.")
            return

        tasks = tasks_result["body"].get("data", [])

        if not tasks:
            print("No chrono tasks found.")
            return

        city_spiders_map = defaultdict(set)

        for task in tasks:
            city = task.get("city")
            spider = task.get("spider")

            if not city:
                continue

            city = city.strip()

            if spider:
                city_spiders_map[city].add(spider.strip())
            else:
                city_spiders_map[city] = set()

        if not city_spiders_map:
            print("No valid cities found in chrono tasks.")
            return

        print("Cities to scrape:", list(city_spiders_map.keys()))

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []

            for city, spiders in city_spiders_map.items():
                spiders_list = list(spiders) if spiders else None

                future = executor.submit(
                    self.client.run_spiders,
                    city=city,
                    spiders=spiders_list
                )

                futures.append((city, future))

            for city, future in futures:
                try:
                    result = future.result()
                    print(f"Spider result for {city}:", result)
                except Exception as exc:
                    print(f"Error running spiders for {city}:", exc)

        delete_result = self.client.delete_old_listings()
        print("Delete old listings result:", delete_result)

        print("Scheduled chrono tasks finished.")