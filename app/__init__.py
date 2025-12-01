# app/__init__.py
from flask import Flask
from .db import engine, Base

# 1. import models FIRST
from . import models

# 2. import blueprint
from .web import bp

def create_app():
    print(">>> create_app() starting")

    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev-only-change-me"

    # 3. CREATE TABLES NOW — models are loaded
    print(">>> creating tables")
    Base.metadata.create_all(bind=engine)

    # 4. import route modules so decorators attach
    print(">>> importing web routes")
    from .web import routes   # noqa: F401
    from .web import products # noqa: F401

    # 5. now register blueprint
    print(">>> registering blueprint")
    app.register_blueprint(bp)

    # debug route listing
    print(">>> ROUTES:")
    for rule in app.url_map.iter_rules():
        print(" -", rule)

    return app
