# app/web/cpe.py

import csv
from io import TextIOWrapper

from flask import request, render_template, redirect, url_for, flash

from . import bp
from app.db import SessionLocal
from app.models import CPEDictionary


# ------------------------------------------------------------
# SHOW UPLOAD FORM
# ------------------------------------------------------------
@bp.route("/cpe/upload", methods=["GET"])
def cpe_upload_form():
    return render_template("cpe_upload.html")


# ------------------------------------------------------------
# PROCESS CSV UPLOAD
# ------------------------------------------------------------
@bp.route("/cpe/upload", methods=["POST"])
def cpe_upload_submit():
    if "file" not in request.files:
        flash("No file uploaded.", "error")
        return redirect(url_for("web.cpe_upload_form"))

    file = request.files["file"]

    if not file.filename.lower().endswith(".csv"):
        flash("Upload must be a CSV file.", "error")
        return redirect(url_for("web.cpe_upload_form"))

    db = SessionLocal()

    try:
        wrapper = TextIOWrapper(file, encoding="utf-8")
        reader = csv.DictReader(wrapper)

        count = 0
        for row in reader:
            entry = CPEDictionary(
                vendor=row.get("vendor", "").strip(),
                product=row.get("product", "").strip(),
                version=row.get("version", "").strip(),
                cpe_uri=row.get("cpe_uri", "").strip(),
            )
            db.add(entry)
            count += 1

        db.commit()
        flash(f"Imported {count} CPE entries.", "success")

    except Exception as e:
        db.rollback()
        flash(f"Error processing CPE CSV: {e}", "error")

    finally:
        db.close()

    return redirect(url_for("web.cpe_upload_form"))
