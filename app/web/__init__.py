# app/web/__init__.py

from flask import Blueprint

# 1️⃣ Create the blueprint FIRST
bp = Blueprint(
    "web",
    __name__,
    template_folder="templates"
)

# 2️⃣ Import route modules AFTER bp exists
from . import routes
from . import products
from . import cpe
