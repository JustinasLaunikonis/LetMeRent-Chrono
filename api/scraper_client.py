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

    def get_new_listings_by_city(self, city, created_after):
        response = requests.get(
            f"{self.base_url}/data",
            params={
                "city": city,
                "created_after": created_after.isoformat(),
                "limit": 1
            },
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