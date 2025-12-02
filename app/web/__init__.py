# app/web/__init__.py

from flask import Blueprint

bp = Blueprint("web", __name__, template_folder="templates")

# Import views AFTER creating bp to avoid circular imports
from . import routes
from . import products
from . import cpe
