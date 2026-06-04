from flask import Flask
from api.extensions import mail
from api.chrono_scheduler import ChronoScheduler
from api.config import (
    MAIL_SERVER,
    MAIL_PORT,
    MAIL_USERNAME,
    MAIL_PASSWORD,
    MAIL_USE_TLS,
    MAIL_USE_SSL,
)


def create_app():
    app = Flask(__name__)

    app.config["MAIL_SERVER"] = MAIL_SERVER
    app.config["MAIL_PORT"] = MAIL_PORT
    app.config["MAIL_USERNAME"] = MAIL_USERNAME
    app.config["MAIL_PASSWORD"] = MAIL_PASSWORD
    app.config["MAIL_USE_TLS"] = MAIL_USE_TLS
    app.config["MAIL_USE_SSL"] = MAIL_USE_SSL

    mail.init_app(app)

    scheduler = ChronoScheduler()

    with app.app_context():
        scheduler.start()

    @app.route("/")
    def index():
        return "Chrono service is running"

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)