#/app/web/__init__.py

print(">>> web/__init__.py running")
from . import routes
print(">>> imported routes")
from . import products
print(">>> imported products")


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

