# app/web/products.py
import csv
from io import TextIOWrapper
from flask import request, render_template, redirect, url_for, flash
from . import bp
from app.db import SessionLocal
from app.models import Product, CPEDictionary

# --- Product list ---
@bp.route("/products")
def products():
    db = SessionLocal()
    rows = db.query(Product).order_by(Product.id).all()
    db.close()
    return render_template("products.html", products=rows)

# --- CSV upload ---
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

# --- Add product form ---
@bp.route("/products/add", methods=["GET"])
def add_product_form():
    db = SessionLocal()
    cpes = db.query(CPEDictionary).order_by(CPEDictionary.vendor, CPEDictionary.product).all()
    db.close()
    return render_template("product_add.html", cpes=cpes)
