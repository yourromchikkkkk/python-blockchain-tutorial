"""
Application factory module.
Creates and configures the Flask application instance.
"""
from flask import Flask
from flask_cors import CORS

from backend.app.routes import register_routes


def create_app():
    """
    Create and configure the Flask application.
    
    Returns:
        Flask application instance with routes and CORS configured
    """
    app = Flask(__name__)

    CORS(
        app,
        resources={
            r"/*": {
                "origins": [
                    "http://localhost:3000",
                    "http://localhost:8080",
                    "http://localhost",
                    # "http://blockchain.test",
                    # "https://*.trycloudflare.com",
                    # TODO: when saving this on MacOS, stop and restart the kubectl tunnels
                    "https://gale-subaru-fax-interventions.trycloudflare.com",
                ]
            }
        },
    )

    register_routes(app)

    return app
