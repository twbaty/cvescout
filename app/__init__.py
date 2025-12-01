# app/__init__.py
from flask import Flask
from .db import engine, Base
from .web import bp as web_bp

def create_app():
    print(">>> create_app() starting")

    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev-only-change-me"

    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    print(">>> registering blueprint")
    app.register_blueprint(web_bp)

    # 🔥 THIS LINE REGISTERS THE PRODUCTS ROUTES
    from .web import products  # noqa: F401

    # Debug: Print all routes loaded
    print(">>> ROUTES:")
    for rule in app.url_map.iter_rules():
        print(" -", rule)

    return app
