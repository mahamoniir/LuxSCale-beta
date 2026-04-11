from flask import Flask, request, jsonify, send_file
import io
from fpdf import FPDF
import json
import os
import numpy as np
import matplotlib.pyplot as plt
import tempfile

# import your existing functions
from luxscale.app_settings import validate_ceiling_height_m
from luxscale.lighting_calc import calculate_lighting, draw_heatmap

app = Flask(__name__)

@app.route("/calculate", methods=["POST"])
def api_calculate():
    data = request.get_json()

    try:
        place = data["place"]
        sides = data["sides"]  # list of 4 floats
        height = float(data["height"])
        ok_h, err_h = validate_ceiling_height_m(height)
        if not ok_h:
            return jsonify({"status": "error", "message": err_h}), 400
        project_info = data["project_info"]  # dict

        results, length, width, _calc_meta = calculate_lighting(place, sides, height)
        return jsonify({
            "status": "success",
            "project_info": project_info,
            "results": results,
            "length": length,
            "width": width
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route("/pdf", methods=["POST"])
def api_pdf():
    data = request.get_json()

    place = data["place"]
    sides = data["sides"]
    height = float(data["height"])
    ok_h, err_h = validate_ceiling_height_m(height)
    if not ok_h:
        return jsonify({"status": "error", "message": err_h}), 400
    project_info = data["project_info"]

    results, length, width, _calc_meta = calculate_lighting(place, sides, height)

    pdf = FPDF(format='A4')
    pdf.add_page()
    pdf.set_font("Arial", size=16)
    pdf.cell(200, 10, "Lighting Design Report", ln=True)
    for k, v in project_info.items():
        pdf.cell(200, 10, f"{k}: {v}", ln=True)

    for res in results:
        pdf.add_page()
        for key, val in res.items():
            pdf.cell(0, 10, f"{key}: {val}", ln=True)

    pdf_bytes = io.BytesIO(pdf.output(dest='S').encode('latin1'))
    pdf_bytes.seek(0)
    return send_file(pdf_bytes, download_name="report.pdf", as_attachment=True)

@app.route("/", methods=["GET"])
def api_index():
    return jsonify({"status": "success", "message": "Welcome to the API"})

if __name__ == "__main__":
    app.run(debug=True)
