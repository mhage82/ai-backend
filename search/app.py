from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from maze_stack import solve_stack
from maze_queue import solve_queue
import os

app = Flask(__name__)
CORS(app)


# Ensure static directory exists
os.makedirs("static", exist_ok=True)

@app.route("/solve", methods=["POST"])
def solve():
    data = request.get_json()
    maze_file = data.get("maze")
    algo = data.get("algorithm")
    full_path = os.path.join("mazes", maze_file)

    if not os.path.exists(full_path):
        return jsonify({"error": "Maze file not found."}), 404

    try:
        if algo == "stack":
            result = solve_stack(full_path)
        elif algo == "queue":
            result = solve_queue(full_path)
        else:
            return jsonify({"error": "Unknown algorithm."}), 400
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/static/<filename>")
def static_file(filename):
    return send_from_directory("static", filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
