import requests

from api.config import SCRAPER_SERVICE_URL, OLD_LISTINGS_DAYS


class ScraperClient:
    def __init__(self):
        # Store the scraper API base URL without a trailing slash
        self.base_url = SCRAPER_SERVICE_URL.rstrip("/")

    def run_spiders(self):
        # Send a POST request to start the spiders
        response = requests.post(f"{self.base_url}/spiders/run", timeout=30)

        # Return the response in a consistent format
        return self._response_data(response)

    def delete_old_listings(self):
        # Send a GET request to delete listings older than the configured number of days
        response = requests.get(
            f"{self.base_url}/listings/old",
            params={
                "days": OLD_LISTINGS_DAYS,
                "dry_run": "false"
            },
            timeout=30
        )

        # Return the response in a consistent format
        return self._response_data(response)

    @staticmethod
    def _response_data(response):
        # Try to parse the response body as JSON
        try:
            body = response.json()

        # If the response is not JSON, use plain text instead
        except ValueError:
            body = response.text

        # Return status code and response body
        return {
            "status_code": response.status_code,
            "body": body
        }