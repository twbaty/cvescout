import csv
from io import TextIOWrapper
from flask import request, render_template, redirect, url_for, flash
from . import bp
from app.db import SessionLocal
from app.models import Product, CPEDictionary

# Temporary tag list (later will come from DB)
TAG_OPTIONS = [
    "server",
    "workstation",
    "critical",
    "internet-facing",
    "high-risk",
    "on-prem",
    "cloud"
]


@bp.route("/products", methods=["GET"])
def products():
    db = SessionLocal()
    rows = db.query(Product).order_by(Product.id).all()
    db.close()
    return render_template("products.html", products=rows)


@bp.route("/products/add", methods=["GET"])
def add_product_form():
    db = SessionLocal()
    cpes = db.query(CPEDictionary).order_by(CPEDictionary.vendor, CPEDictionary.product).all()
    db.close()
    return render_template("products_add.html", cpes=cpes, tags=TAG_OPTIONS)


@bp.route("/products/add", methods=["POST"])
def add_product_submit():
    vendor = request.form.get("vendor", "").strip()
    name = request.form.get("name", "").strip()
    version = request.form.get("version", "").strip()
    cpe_uri = request.form.get("cpe_uri", "").strip()

    selected_tags = request.form.getlist("tags")      # <-- multiple checkboxes
    tag_str = ",".join(selected_tags)

    active = "active" in request.form

    db = SessionLocal()

    try:
        product = Product(
            vendor=vendor,
            name=name,
            version=version,
            cpe_uri=cpe_uri,
            tags=tag_str,
            active=active
        )
        db.add(product)
        db.commit()
        flash("Product added successfully.", "success")

    except Exception as e:
        db.rollback()
        flash(f"Error saving product: {e}", "error")

    finally:
        db.close()

    return redirect(url_for("web.products"))
