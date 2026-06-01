import requests

from api.config import SCRAPER_SERVICE_URL, OLD_LISTINGS_DAYS


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