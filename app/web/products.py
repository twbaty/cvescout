# app/web/products.py
import csv
from io import TextIOWrapper
from flask import request, render_template, redirect, url_for, flash
from . import bp
from app.db import SessionLocal
from app.models import Product, CPEDictionary


# -------------------------------------------------
# LIST PRODUCTS
# -------------------------------------------------
@bp.route("/products", methods=["GET"])
def products():
    db = SessionLocal()
    items = db.query(Product).order_by(Product.id).all()
    db.close()
    return render_template("products.html", products=items)


# -------------------------------------------------
# ADD PRODUCT (FORM)
# -------------------------------------------------
@bp.route("/products/add", methods=["GET"])
def add_product_form():
    db = SessionLocal()
    cpes = (
        db.query(CPEDictionary)
        .order_by(CPEDictionary.vendor, CPEDictionary.product)
        .all()
    )
    db.close()
    return render_template("product_add.html", cpes=cpes)


# -------------------------------------------------
# ADD PRODUCT (POST)
# -------------------------------------------------
@bp.route("/products/add", methods=["POST"])
def add_product_post():
    name = request.form.get("name", "").strip()
    vendor = request.form.get("vendor", "").strip()
    version = request.form.get("version", "").strip()
    cpe_uri = request.form.get("cpe_uri", "")
    tags = request.form.get("tags", "").strip()

    if not name or not vendor:
        flash("Name and vendor are required.", "error")
        return redirect(url_for("web.add_product_form"))

    db = SessionLocal()
    try:
        p = Product(
            name=name,
            vendor=vendor,
            version=version,
            cpe_uri=cpe_uri,
            tags=tags,
            active=True,
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


# -------------------------------------------------
# CSV UPLOAD (unchanged, works fine)
# -------------------------------------------------
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
                active=row.get("active", "true").lower() in ("true", "1", "yes"),
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
