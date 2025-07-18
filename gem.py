# app.py
from flask import Flask, request, jsonify, render_template
from gemini_handler import get_gemini_response

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("gem.html")

@app.route("/gemini", methods=["POST"])
def gemini():
    data = request.get_json()
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "No input text provided"}), 400

    response = get_gemini_response(text)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True, port=5000)