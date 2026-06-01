from flask import Blueprint, jsonify

from api.scheduler import ChronoScheduler

api = Blueprint("api", __name__)
chrono = ChronoScheduler()


@api.get("/health")
def health():
    return jsonify({"status": "chrono-service is running"})


@api.get("/run-now")
def run_now():
    chrono.run_tasks()

    return jsonify({
        "message": "Scheduled chrono tasks executed manually."
    })