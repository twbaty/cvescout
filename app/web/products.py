# app/web/products.py

from flask import request, render_template, redirect, url_for, flash
from app.db import SessionLocal
from app.models import Product, CPEDictionary
from . import bp

# -------------------------------
# NEW: Show checkbox UI
# -------------------------------
@bp.route("/products/select", methods=["GET"])
def select_products():
    db = SessionLocal()

    cpes = db.query(CPEDictionary).order_by(
        CPEDictionary.vendor,
        CPEDictionary.product,
        CPEDictionary.version
    ).all()

    # fetch existing products so we can pre-check boxes
    selected_cpes = {p.cpe_uri for p in db.query(Product).all()}

    db.close()
    return render_template(
        "products_select.html",
        cpes=cpes,
        selected_cpes=selected_cpes
    )

# -------------------------------
# NEW: Handle form POST
# -------------------------------
@bp.route("/products/select", methods=["POST"])
def select_products_submit():
    db = SessionLocal()

    # grab list of all checked CPE URIs
    chosen = request.form.getlist("cpe_uri")

    # wipe old selected results
    db.query(Product).delete()

    # recreate entries
    for uri in chosen:
        p = Product(
            vendor=uri.split(":")[3] if ":" in uri else "",
            name=uri.split(":")[4] if ":" in uri else "",
            version=uri.split(":")[5] if ":" in uri else "",
            cpe_uri=uri,
            active=True
        )
        db.add(p)

    db.commit()
    db.close()

    flash("Selections saved.", "success")
    return redirect(url_for("web.products"))
