# app/web/products.py
import csv
from io import TextIOWrapper
from flask import request, render_template, redirect, url_for, flash
from . import bp
from app.db import SessionLocal
from app.models import Product, CPEDictionary


# ------------------------------------------------------
# LIST PRODUCTS
# ------------------------------------------------------
@bp.route("/products", strict_slashes=False)
def products():
    db = SessionLocal()
    rows = db.query(Product).order_by(Product.id).all()
    db.close()
    return render_template("products.html", products=rows)


# ------------------------------------------------------
# SHOW ADD PRODUCT FORM
# ------------------------------------------------------
@bp.route("/products/add", methods=["GET"])
def add_product_form():
    db = SessionLocal()
    cpes = db.query(CPEDictionary).order_by(CPEDictionary.vendor, CPEDictionary.product).all()
    db.close()

    return render_template("product_add.html", cpes=cpes)


# ------------------------------------------------------
# HANDLE ADD PRODUCT FORM SUBMIT
# ------------------------------------------------------
@bp.route("/products/add", methods=["POST"])
def add_product_submit():
    db = SessionLocal()

    name = request.form.get("name", "").strip()
    vendor = request.form.get("vendor", "").strip()
    version = request.form.get("version", "").strip()
    cpe_uri = request.form.get("cpe_uri", "").strip()
    tags = request.form.get("tags", "").strip()
    active = request.form.get("active") == "on"

    if not name or not vendor:
        flash("Vendor and Name are required.", "error")
        return redirect(url_for("web.add_product_form"))

    p = Product(
        name=name,
        vendor=vendor,
        version=version,
        cpe_uri=cpe_uri,
        tags=tags,
        active=active
    )
    db.add(p)
    db.commit()
    db.close()

    flash("Product added!", "success")
    return redirect(url_for("web.products"))
