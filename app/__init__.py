# app/__init__.py
from flask import Flask
from .db import engine, Base
from .web import bp as web_bp

def create_app():
    print(">>> create_app() starting")

    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev-only-change-me"

    # --- Make sure tables exist BEFORE importing routes that query them ---
    print(">>> creating tables")
    Base.metadata.create_all(bind=engine)

    # --- Register blueprints AFTER tables exist ---
    print(">>> registering blueprint")
    app.register_blueprint(web_bp)

    return app
