from flask import Flask

from api.routes import api
from api.scheduler import ChronoScheduler


def create_app():
    app = Flask(__name__)
    app.register_blueprint(api)

    scheduler = ChronoScheduler()
    scheduler.start()

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)