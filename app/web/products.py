#app/web/products.py
import csv
from io import TextIOWrapper, StringIO
from flask import request, render_template, redirect, url_for, flash, Response

from . import bp
from app.db import SessionLocal
from app.models import Product, CPEDictionary


# ---------------------------------------------------------
# EXPORT PRODUCTS AS CSV
# ---------------------------------------------------------
@bp.route("/products/export", methods=["GET"])
def export_products():
    db = SessionLocal()
    rows = db.query(Product).order_by(Product.id).all()
    db.close()

    si = StringIO()
    writer = csv.writer(si)

    writer.writerow(["id", "vendor", "name", "version", "cpe_uri", "tags", "active"])

    for p in rows:
        writer.writerow([
            p.id,
            p.vendor,
            p.name,
            p.version,
            p.cpe_uri,
            p.tags,
            "yes" if p.active else "no"
        ])

    return Response(
        si.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=products_export.csv"}
    )


# ---------------------------------------------------------
# LIST PRODUCTS
# ---------------------------------------------------------
@bp.route("/products", methods=["GET"])
def products():
    db = SessionLocal()
    rows = db.query(Product).order_by(Product.id).all()
    db.close()
    return render_template("products.html", products=rows)


# =========================================================
# SELECT PRODUCTS FROM CPE DICTIONARY (CHECKBOX UI)
# =========================================================

# --- GET FORM ---
@bp.route("/products/select", methods=["GET"])
def select_products():
    db = SessionLocal()
    cpes = (
        db.query(CPEDictionary)
        .order_by(CPEDictionary.vendor, CPEDictionary.product, CPEDictionary.version)
        .all()
    )

    # currently selected (active) products
    active = {
        p.cpe_uri
        for p in db.query(Product).filter(Product.active == True).all()
    }

    db.close()

    return render_template(
        "product_select.html",
        cpes=cpes,
        selected_cpes=active
    )


# --- POST SUBMIT ---
@bp.route("/products/select/submit", methods=["POST"])
def select_products_submit():
    chosen = set(request.form.getlist("cpe_uri"))

    db = SessionLocal()
    try:
        # map existing
        existing = {
            p.cpe_uri: p
            for p in db.query(Product).filter(Product.cpe_uri.isnot(None)).all()
        }

        # Activate or create chosen
        for uri in chosen:
            if uri in existing:
                existing[uri].active = True
                continue

            c = db.query(CPEDictionary).filter_by(cpe_uri=uri).first()
            if c:
                db.add(Product(
                    vendor=c.vendor,
                    name=c.product,
                    version=c.version,
                    cpe_uri=c.cpe_uri,
                    tags="",
                    active=True
                ))

        # Deactivate unchosen
        for uri, prod in existing.items():
            if uri not in chosen:
                prod.active = False

        db.commit()
        flash("Product selection updated.", "success")

    except Exception as e:
        db.rollback()
        flash(f"Error saving selection: {e}", "error")

    finally:
        db.close()

    return redirect(url_for("web.products"))


# ---------------------------------------------------------
# ADD PRODUCT (MANUAL ENTRY)
# ---------------------------------------------------------
@bp.route("/products/add", methods=["GET"])
def add_product_form():
    db = SessionLocal()
    cpes = (
        db.query(CPEDictionary)
        .order_by(CPEDictionary.vendor, CPEDictionary.product, CPEDictionary.version)
        .all()
    )
    db.close()
    return render_template("products_add.html", cpes=cpes)


@bp.route("/products/add", methods=["POST"])
def add_product_submit():
    vendor = request.form.get("vendor", "").strip()
    name = request.form.get("name", "").strip()
    version = request.form.get("version", "").strip()
    cpe_uri = request.form.get("cpe_uri", "").strip()
    tags = request.form.get("tags", "").strip()
    active = request.form.get("active") == "on"

    if not vendor or not name:
        flash("Vendor and Name are required.", "error")
        return redirect(url_for("web.add_product_form"))

    db = SessionLocal()
    try:
        db.add(Product(
            vendor=vendor,
            name=name,
            version=version,
            cpe_uri=cpe_uri,
            tags=tags,
            active=active
        ))
        db.commit()
        flash("Product added.", "success")

    except Exception as e:
        db.rollback()
        flash(f"Error adding product: {e}", "error")

    finally:
        db.close()

    return redirect(url_for("web.products"))


# ---------------------------------------------------------
# BULK UPLOAD CSV
# ---------------------------------------------------------
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
            db.add(Product(
                vendor=row.get("vendor", "").strip(),
                name=row.get("name", "").strip(),
                version=row.get("version", "").strip(),
                cpe_uri=row.get("cpe_uri", "").strip(),
                tags=row.get("tags", "").strip(),
                active=row.get("active", "yes").lower() in ("true", "1", "yes")
            ))

        db.commit()
        flash("Products uploaded successfully.", "success")

    except Exception as e:
        db.rollback()
        flash(f"Error processing CSV: {e}", "error")

    finally:
        db.close()

    return redirect(url_for("web.products"))
