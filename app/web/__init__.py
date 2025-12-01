# app/web/__init__.py
from flask import Blueprint

bp = Blueprint(
    "web",
    __name__,
    template_folder="templates"
)

from . import routes  # noqa: E402
