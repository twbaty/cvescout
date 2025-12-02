# app/web/products.py

import csv
from io import TextIOWrapper

from flask import request, render_template, redirect, url_for, flash

from . import bp
from app.db import SessionLocal
from app.models import Product, CPEDictionary

# ----------------------------------------------------------------------
# EXPORT PRODUCTS AS CSV
# ----------------------------------------------------------------------
@bp.route("/products/export", methods=["GET"])
def export_products():
    db = SessionLocal()
    rows = db.query(Product).order_by(Product.id).all()
    db.close()

    # Build CSV content
    import csv
    from io import StringIO
    si = StringIO()
    writer = csv.writer(si)

    # header row
    writer.writerow(["id", "vendor", "name", "version", "cpe_uri", "tags", "active"])

    # data rows
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

    output = si.getvalue()
    si.close()

    # Return file download
    from flask import Response
    return Response(
        output,
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=products_export.csv"
        }
    )

# ----------------------------------------------------------------------
# LIST PRODUCTS
# ----------------------------------------------------------------------
@bp.route("/products", methods=["GET"])
def products():
    db = SessionLocal()
    try:
        rows = db.query(Product).order_by(Product.id).all()
    finally:
        db.close()

    return render_template("products.html", products=rows)


# ----------------------------------------------------------------------
# SELECT PRODUCTS (checkbox UI backed by CPEDictionary)
# ----------------------------------------------------------------------
@bp.route("/products/select", methods=["POST"])
def select_products_submit():
    selected = request.form.getlist("cpe_uri")

    db = SessionLocal()

    # Clear existing products
    db.query(Product).delete()

    # Insert new selections
    for uri in selected:
        c = db.query(CPEDictionary).filter_by(cpe_uri=uri).first()
        if c:
            db.add(Product(
                vendor=c.vendor,
                name=c.product,
                version=c.version,
                cpe_uri=c.cpe_uri,
                tags="",        # you can populate later
                active=True
            ))

    db.commit()
    db.close()

    return redirect(url_for("web.products"))





@bp.route("/products/select/submit", methods=["POST"])
def select_products_submit():
    # All CPEs the user checked in the form
    chosen_cpes = set(request.form.getlist("cpe_uri"))

    db = SessionLocal()
    try:
        # Map existing products by cpe_uri
        existing = {
            p.cpe_uri: p
            for p in db.query(Product).filter(Product.cpe_uri.isnot(None)).all()
        }

        # Turn ON / create for all selected CPEs
        for cpe in chosen_cpes:
            if not cpe:
                continue

            if cpe in existing:
                # Already in products → just make sure it's active
                existing[cpe].active = True
                continue

            # Not in products yet → create from CPEDictionary
            cpe_row = db.query(CPEDictionary).filter_by(cpe_uri=cpe).first()
            if not cpe_row:
                # Shouldn't happen if DB is consistent, but don't blow up
                continue

            p = Product(
                vendor=cpe_row.vendor or "",
                name=cpe_row.product or "",
                version=cpe_row.version or "",
                cpe_uri=cpe_row.cpe_uri,
                tags="",        # you can enrich later
                active=True,
            )
            db.add(p)

        # Turn OFF anything that is no longer selected
        for cpe, prod in existing.items():
            if cpe not in chosen_cpes:
                prod.active = False

        db.commit()
        flash("Product selection updated.", "success")

    except Exception as e:
        db.rollback()
        flash(f"Error saving selection: {e}", "error")

    finally:
        db.close()

    return redirect(url_for("web.products"))


# ----------------------------------------------------------------------
# ADD PRODUCT (manual single record)
# ----------------------------------------------------------------------
@bp.route("/products/add", methods=["GET"])
def add_product_form():
    db = SessionLocal()
    try:
        cpes = (
            db.query(CPEDictionary)
            .order_by(CPEDictionary.vendor, CPEDictionary.product, CPEDictionary.version)
            .all()
        )
    finally:
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
        p = Product(
            vendor=vendor,
            name=name,
            version=version,
            cpe_uri=cpe_uri,
            tags=tags,
            active=active,
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
