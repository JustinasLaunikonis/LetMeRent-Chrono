from flask import Flask

from api.routes import api
from api.scheduler import ChronoScheduler


def create_app():
    # Create Flask application instance
    app = Flask(__name__)

    # Register API routes blueprint
    app.register_blueprint(api)

    # Create scheduler instance
    scheduler = ChronoScheduler()

    # Start background scheduler
    scheduler.start()

    # Return configured Flask app
    return app


# Create the Flask application
app = create_app()


if __name__ == "__main__":
    # Run the application only when this file is executed directly
    app.run(host="0.0.0.0", port=5001)