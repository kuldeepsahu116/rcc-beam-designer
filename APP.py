from flask import Flask, render_template, request, jsonify
from beam_design import design_beam   # <-- your function

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/design", methods=["POST"])
def design():
    data = request.json            # data coming from HTML (JavaScript)
    result = design_beam(data)     # calling your RCC code
    return jsonify(result)         # sending result back to UI

if __name__ == "__main__":
    app.run(debug=True)