from flask import Flask, render_template, request, jsonify
from simulator.cache import run_hierarchy, compare_algorithms

app = Flask(__name__)

@app.get("/")
def home():
    return render_template("index.html")

@app.post("/api/simulate")
def simulate():
    try:
        return jsonify(success=True, result=run_hierarchy(request.get_json(silent=True) or {}))
    except (ValueError, TypeError) as exc:
        return jsonify(success=False, error=str(exc)), 400

@app.post("/api/compare")
def compare():
    try:
        return jsonify(success=True, result=compare_algorithms(request.get_json(silent=True) or {}))
    except (ValueError, TypeError) as exc:
        return jsonify(success=False, error=str(exc)), 400

@app.get("/health")
def health():
    return jsonify(status="ok", app="MemoryLab")

if __name__ == "__main__":
    app.run(debug=True)
