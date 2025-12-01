# app/__init__.py
from flask import Flask
from .db import engine, Base
from .web import bp  # import the blueprint object

def create_app():
    print(">>> create_app() starting")

    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev-only-change-me"

    Base.metadata.create_all(bind=engine)

    print(">>> importing web modules before registering blueprint")

    # IMPORTANT: import all modules that define routes BEFORE registering bp
    from .web import routes      # noqa: F401
    from .web import products    # noqa: F401

    print(">>> registering blueprint")
    app.register_blueprint(bp)

    print(">>> ROUTES:")
    for rule in app.url_map.iter_rules():
        print(" -", rule)

    return app
