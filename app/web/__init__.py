print(">>> web/__init__.py running")

from flask import Blueprint

# Create ONE blueprint
bp = Blueprint(
    "web",
    __name__,
    template_folder="templates"
)

# Import routes so they get attached to bp
print(">>> importing route handlers")
from . import routes

print(">>> importing product handlers")
from . import products
