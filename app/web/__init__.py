#/app/web/__init__.py
from flask import Blueprint

bp = Blueprint(
    "web",
    __name__,
    template_folder="templates"
)

# Must be FIRST import
from . import routes

# Other modules AFTER routes
from . import products
