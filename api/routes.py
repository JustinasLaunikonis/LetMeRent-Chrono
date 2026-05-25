from flask import Blueprint, jsonify

from api.scraper_client import ScraperClient

api = Blueprint("api", __name__)
client = ScraperClient()


@api.get("/health")
def health():
    return jsonify({"status": "chrono-service is running"})


@api.get("/run-now")
def run_now():
    spiders_result = client.run_spiders()
    delete_result = client.delete_old_listings()

    return jsonify({
        "message": "Tasks executed manually.",
        "spiders_result": spiders_result,
        "delete_result": delete_result
    })