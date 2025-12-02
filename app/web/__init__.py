# app/web/__init__.py

print(">>> web/__init__.py running")

# Import routes BEFORE creating the Blueprint
# so that routes can safely import bp afterward

def register_routes(bp):
    print(">>> importing route handlers")
    from . import routes

    print(">>> importing product handlers")
    from . import products


# Create the blueprint AFTER the importable function is defined
from flask import Blueprint
bp = Blueprint(
    "web",
    __name__,
    template_folder="templates"
)

# Now register all routes
register_routes(bp)
