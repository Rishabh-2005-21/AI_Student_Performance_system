"""Flask entry point for AI student performance system."""

from __future__ import annotations

import os
from dotenv import load_dotenv

load_dotenv()


from flask import Flask, send_from_directory
from flask_cors import CORS

from routes.api_routes import api_bp
import db_mongo


BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
CLIENT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "client"))


def create_app() -> Flask:
    app = Flask(__name__, static_folder=CLIENT_DIR, static_url_path="")
    CORS(app)
    app.register_blueprint(api_bp)

    # Initialise MongoDB and seed default users
    db_mongo.init_mongo()

    @app.get("/")
    def root():
        return send_from_directory(CLIENT_DIR, "index.html")

    # All client-side routes fall through to index.html (React Router handles them)
    @app.get("/<path:path>")
    def catch_all(path):
        return send_from_directory(CLIENT_DIR, "index.html")

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)