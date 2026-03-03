from flask import Flask, render_template, request, jsonify
from beam_design import design_beam   # <-- your function

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/design", methods=["POST"])
def design():
    raw = request.get_json()

    try:
        data = {
            "moment": float(raw["moment"]),
            "shear": float(raw["shear"]),
            "width": float(raw["width"]),
            "fck": float(raw["fck"]),
            "fy": float(raw["fy"]),
            "clear_cover": float(raw["clear_cover"]),
            "side_cover": float(raw["side_cover"])
        }
    except:
        return jsonify({"error": "Invalid or empty input"}), 400

    result = design_beam(data)
    return jsonify(result)     # sending result back to UI

if __name__ == "__main__":
    app.run(debug=True)