# app/web/__init__.py

print(">>> web/__init__.py running")

from flask import Blueprint

# Create the blueprint
bp = Blueprint(
    "web",
    __name__,
    template_folder="templates"
)

print(">>> web/__init__.py: importing routes")
from . import routes     # defines '/' and other basic pages

print(">>> web/__init__.py: importing products")
from . import products   # defines /products and upload handlers
