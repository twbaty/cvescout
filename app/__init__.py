# app/__init__.py
from flask import Flask
from .db import engine, Base
from .web import bp as web_bp

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev-only-change-me"

    Base.metadata.create_all(bind=engine)

    app.register_blueprint(web_bp)

    return app
