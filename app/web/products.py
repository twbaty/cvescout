# app/web/products.py

import csv
from io import TextIOWrapper
from flask import request, render_template, redirect, url_for, flash

from . import bp
from app.db import SessionLocal
from app.models import Product, CPEDictionary


# ----------------------------------------------------------------------
# LIST PRODUCTS
# ----------------------------------------------------------------------
@bp.route("/products", methods=["GET"])
def products():
    db = SessionLocal()
    rows = db.query(Product).order_by(Product.id).all()
    db.close()
    return render_template("products.html", products=rows)


# ----------------------------------------------------------------------
# ADD PRODUCT (GET form)
# ----------------------------------------------------------------------
@bp.route("/products/add", methods=["GET"])
def add_product_form():
    db = SessionLocal()
    cpes = db.query(CPEDictionary).order_by(
        CPEDictionary.vendor,
        CPEDictionary.product,
        CPEDictionary.version
    ).all()
    db.close()

    return render_template("products_add.html", cpes=cpes)


# ----------------------------------------------------------------------
# ADD PRODUCT (POST submit)
# ----------------------------------------------------------------------
@bp.route("/products/add", methods=["POST"])
def add_product_submit():
    vendor = request.form.get("vendor", "").strip()
    name   = request.form.get("name", "").strip()
    version = request.form.get("version", "").strip()
    cpe_uri = request.form.get("cpe_uri", "").strip()
    tags = request.form.get("tags", "").strip()
    active = request.form.get("active") == "on"

    if not vendor or not name:
        flash("Vendor and Name are required.", "error")
        return redirect(url_for("web.add_product_form"))

    db = SessionLocal()

    try:
        p = Product(
            vendor=vendor,
            name=name,
            version=version,
            cpe_uri=cpe_uri,
            tags=tags,
            active=active
        )
        db.add(p)
        db.commit()
        flash("Product added.", "success")

    except Exception as e:
        db.rollback()
        flash(f"Error adding product: {e}", "error")

    finally:
        db.close()

    return redirect(url_for("web.products"))


# ----------------------------------------------------------------------
# BULK UPLOAD CSV
# ----------------------------------------------------------------------
@bp.route("/products/upload", methods=["POST"])
def upload_products():
    if "file" not in request.files:
        flash("No file uploaded.", "error")
        return redirect(url_for("web.products"))

    file = request.files["file"]
    if file.filename == "":
        flash("Empty filename.", "error")
        return redirect(url_for("web.products"))

    db = SessionLocal()

    try:
        wrapper = TextIOWrapper(file, encoding="utf-8")
        reader = csv.DictReader(wrapper)

        for row in reader:
            product = Product(
                name=row.get("name", "").strip(),
                vendor=row.get("vendor", "").strip(),
                version=row.get("version", "").strip(),
                cpe_uri=row.get("cpe_uri", "").strip(),
                tags=row.get("tags", "").strip(),
                active=row.get("active", "true").lower() in ("true", "1", "yes")
            )
            db.add(product)

        db.commit()
        flash("Products uploaded successfully.", "success")

    except Exception as e:
        db.rollback()
        flash(f"Error processing CSV: {e}", "error")

    finally:
        db.close()

    return redirect(url_for("web.products"))
