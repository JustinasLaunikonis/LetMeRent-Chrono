import requests

from api.config import SCRAPER_SERVICE_URL, OLD_LISTINGS_DAYS
import time


class ScraperClient:
    def __init__(self):
        self.base_url = SCRAPER_SERVICE_URL.rstrip("/")

    def get_chrono_tasks(self):
        response = requests.get(
            f"{self.base_url}/chrono/tasks",
            params={"limit": 500},
            timeout=30
        )
        return self._response_data(response)

    def get_spider_job(self, job_id):
        response = requests.get(
            f"{self.base_url}/spiders/jobs/{job_id}",
            timeout=30
        )

        return self._response_data(response)

    def wait_for_spider_job(self, job_id):
        print(f"Waiting for spider job {job_id}")
        while True:
            result = self.get_spider_job(job_id)

            print("Job status result:", result)

            if result["status_code"] != 200:
                return result

            status = result["body"]["job"]["status"]

            if status == "completed":
                return result

            if status == "failed":
                return result

            time.sleep(5)

    def run_spiders(self, city=None, spiders=None):
        payload = {}

        if city:
            payload["city"] = city

        if spiders:
            payload["spiders"] = spiders

        response = requests.post(
            f"{self.base_url}/spiders/run",
            json=payload,
            timeout=30
        )

        return self._response_data(response)

    def delete_old_listings(self):
        response = requests.get(
            f"{self.base_url}/listings/old",
            params={
                "days": OLD_LISTINGS_DAYS,
                "dry_run": "false"
            },
            timeout=30
        )

        return self._response_data(response)

    def get_listings_by_city(self, city):
        response = requests.get(
            f"{self.base_url}/data",
            params={
                "city": city,
                "limit": 1
            },
            timeout=30
        )

        return self._response_data(response)

    def get_matching_new_listings(self, task, created_after):
        params = {
            "city": task.get("city"),
            "created_after": created_after.isoformat(),
            "limit": 10,
            "sort": "created_at",
            "order": "desc",
        }

        if task.get("min_budget") is not None:
            params["min_price"] = task["min_budget"]

        if task.get("max_budget") is not None:
            params["max_price"] = task["max_budget"]

        if task.get("room_type"):
            params["room_type"] = task["room_type"]

        if task.get("furnishing"):
            params["furnishing"] = task["furnishing"]

        if task.get("pet_friendly") is not None:
            params["pet_friendly"] = str(task["pet_friendly"]).lower()

        response = requests.get(
            f"{self.base_url}/data",
            params=params,
            timeout=30
        )

        return self._response_data(response)

    def get_user_by_username(self, username):
        response = requests.get(
            f"{self.base_url}/users/by-username/{username}",
            timeout=30
        )

        return self._response_data(response)

    @staticmethod
    def _response_data(response):
        try:
            body = response.json()
        except ValueError:
            body = response.text

        return {
            "status_code": response.status_code,
            "body": body
        }