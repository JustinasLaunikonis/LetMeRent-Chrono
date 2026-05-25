import requests

from api.config import SCRAPER_SERVICE_URL, OLD_LISTINGS_DAYS


class ScraperClient:
    def __init__(self):
        self.base_url = SCRAPER_SERVICE_URL.rstrip("/")

    def run_spiders(self):
        response = requests.post(f"{self.base_url}/spiders/run", timeout=30)
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