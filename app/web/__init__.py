# app/web/__init__.py
from flask import Blueprint

bp = Blueprint(
    "web",
    __name__,
    template_folder="templates"
)

from . import routes  # noqa: E402

# app/web/__init__.py
from flask import Blueprint

bp = Blueprint(
    "web",
    __name__,
    template_folder="templates"
)

# Load ALL route modules BEFORE blueprint is registered
from . import routes
from . import products
