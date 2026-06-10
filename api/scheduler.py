from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

from apscheduler.schedulers.background import BackgroundScheduler

from api.config import SCHEDULER_INTERVAL_MINUTES
from api.scraper_client import ScraperClient
from api.email_client import EmailClient
from datetime import datetime, timezone


class ChronoScheduler:
    def __init__(self, app=None):
        self.app = app
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
            username = task.get("user")
            city = task.get("city")

            if not username or not city:
                continue

            username = username.strip()
            city = city.strip()

            pair = (username, city.lower())

            if pair in sent_pairs:
                continue

            user_result = self.client.get_user_by_username(username)

            if user_result["status_code"] != 200:
                print(f"Could not find user by username: {username}")
                continue

            user_email = user_result["body"]["user"].get("email")

            if not user_email:
                print(f"User {username} has no email")
                continue

            listings_result = self.client.get_matching_new_listings(
                task=task,
                created_after=started_at
            )

            if listings_result["status_code"] != 200:
                print(f"Could not check listings for user {username}")
                continue

            listings = listings_result["body"].get("data", [])

            if not listings:
                print(f"No matching listings for {username}")
                continue

            links = []

            for listing in listings[:10]:
                link = (
                        listing.get("url")
                        or listing.get("link")
                        or listing.get("listing_url")
                        or listing.get("detail_url")
                )

                if link:
                    links.append(link)

            if not links:
                print(f"Listings found but no links for {username}")
                continue

            subject = "LetMeRent notification"

            body = f"Hi {username},\n\n"
            body += (
                f"We found new housing listings in {city} "
                f"that match your requirements:\n\n"
            )

            for index, link in enumerate(links, start=1):
                body += f"{index}. {link}\n"

            body += "\nKind regards,\nLetMeRent"

            try:
                if self.app:
                    with self.app.app_context():
                        self.email_client.send_email(
                            to_email=user_email,
                            subject=subject,
                            body=body
                        )
                else:
                    self.email_client.send_email(
                        to_email=user_email,
                        subject=subject,
                        body=body
                    )

                sent_pairs.add(pair)
                print(f"Email sent to {user_email}")

            except Exception as exc:
                print(f"Error sending email to {user_email}: {exc}")

    def run_and_wait_for_city(self, city, spiders_list):
        print(f"Starting spider for {city}")
        result = self.client.run_spiders(
            city=city,
            spiders=spiders_list
        )
        print(f"Run spider response for {city}:", result)

        if result["status_code"] != 202:
            return result

        job_id = result["body"]["job"]["id"]
        print(f"Waiting for job {job_id} for city {city}")

        final_result = self.client.wait_for_spider_job(job_id)

        print(f"Final spider result for {city}:", final_result)

        return final_result

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