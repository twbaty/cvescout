# app/web/products.py
import csv
from io import TextIOWrapper
from flask import request, render_template, redirect, url_for, flash
from . import bp
from app.db import SessionLocal
from app.models import Product, CPEDictionary


@bp.route("/products", strict_slashes=False)
def products():
    db = SessionLocal()
    rows = db.query(Product).order_by(Product.id).all()
    db.close()
    return render_template("products.html", products=rows)


# -------------------------------
# Add Product (GET)
# -------------------------------
@bp.route("/products/add", methods=["GET"])
def add_product_form():
    db = SessionLocal()
    cpes = db.query(CPEDictionary).order_by(
        CPEDictionary.vendor,
        CPEDictionary.product
    ).all()
    db.close()

    return render_template("product_add.html", cpes=cpes)


# -------------------------------
# Add Product (POST)
# -------------------------------
@bp.route("/products/add", methods=["POST"])
def add_product_post():
    vendor = request.form.get("vendor", "").strip()
    name = request.form.get("name", "").strip()
    version = request.form.get("version", "").strip()
    cpe_uri = request.form.get("cpe_uri", "").strip()
    tags = request.form.get("tags", "").strip()
    active = "active" in request.form

    if not vendor or not name:
        flash("Vendor and name are required.", "error")
        return redirect(url_for("web.add_product_form"))

    db = SessionLocal()
    try:
        p = Product(
            vendor=vendor,
            name=name,
            version=version,
            cpe_uri=cpe_uri if cpe_uri else None,
            tags=tags,
            active=active
        )
        db.add(p)
        db.commit()

        flash("Product added.", "success")

    except Exception as e:
        db.rollback()
        flash(f"Error: {e}", "error")

    finally:
        db.close()

    return redirect(url_for("web.products"))
