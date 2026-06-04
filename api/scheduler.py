from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

from apscheduler.schedulers.background import BackgroundScheduler

from api.config import SCHEDULER_INTERVAL_MINUTES
from api.scraper_client import ScraperClient
from api.email_client import EmailClient
from datetime import datetime, timezone


class ChronoScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.client = ScraperClient()
        self.email_client = EmailClient()

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

        started_at = datetime.now(timezone.utc)

        tasks_result = self.client.get_chrono_tasks()
        print("Chrono tasks result:", tasks_result)

        if tasks_result["status_code"] != 200:
            print("Could not fetch chrono tasks.")
            return

        tasks = tasks_result["body"].get("data", [])

        if not tasks:
            print("No chrono tasks found.")
            return

        city_spiders_map = self.group_tasks_by_city(tasks)

        if not city_spiders_map:
            print("No valid cities found in chrono tasks.")
            return

        print("Cities to scrape:", list(city_spiders_map.keys()))

        self.run_spiders_for_cities(city_spiders_map)

        self.send_city_emails(tasks, started_at)

        delete_result = self.client.delete_old_listings()
        print("Delete old listings result:", delete_result)

        print("Scheduled chrono tasks finished.")

    def send_city_emails(self, tasks, started_at):
        sent_pairs = set()

        for task in tasks:
            user_email = task.get("user")
            city = task.get("city")

            if not user_email or not city:
                continue

            user_email = user_email.strip()
            city = city.strip()

            pair = (user_email, city.lower())

            if pair in sent_pairs:
                continue

            listings_result = self.client.get_new_listings_by_city(
                city=city,
                created_after=started_at
            )

            if listings_result["status_code"] != 200:
                print(f"Could not check new listings for city {city}")
                continue

            listings_count = listings_result["body"].get("count", 0)

            if listings_count <= 0:
                print(f"No new listings found for city {city}. Email not sent.")
                continue

            subject = "LetMeRent notification"
            body = f"New housing found in city: {city}"

            try:
                self.email_client.send_email(
                    to_email=user_email,
                    subject=subject,
                    body=body
                )

                sent_pairs.add(pair)
                print(f"Email sent to {user_email} for city {city}")

            except Exception as exc:
                print(f"Error sending email to {user_email} for city {city}: {exc}")

    def run_and_wait_for_city(self, city, spiders_list):
        result = self.client.run_spiders(
            city=city,
            spiders=spiders_list
        )

        if result["status_code"] != 202:
            return result

        job_id = result["body"]["job"]["id"]

        return self.client.wait_for_spider_job(job_id)

    @staticmethod
    def group_tasks_by_city(tasks):
        city_spiders_map = defaultdict(set)

        for task in tasks:
            city = task.get("city")
            spider = task.get("spider")

            if not city:
                continue

            city = city.strip()

            if not city:
                continue

            if spider:
                city_spiders_map[city].add(spider.strip())
            else:
                city_spiders_map[city] = set()

        return city_spiders_map

    def run_spiders_for_cities(self, city_spiders_map):
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []

            for city, spiders in city_spiders_map.items():
                spiders_list = list(spiders) if spiders else None

                future = executor.submit(
                    self.run_and_wait_for_city,
                    city,
                    spiders_list
                )

                futures.append((city, future))

            for city, future in futures:
                try:
                    result = future.result()
                    print(f"Spider result for {city}:", result)
                except Exception as exc:
                    print(f"Error running spiders for {city}:", exc)