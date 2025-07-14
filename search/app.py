from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import os
from maze_solver import Maze
from maze_stack import solve_stack
from maze_queue import solve_queue
import os

app = Flask(__name__)
CORS(app)


# Ensure static directory exists
os.makedirs("static", exist_ok=True)

@app.route("/maze-image/<maze>")
def maze_image(maze):
    if not maze.endswith(".txt"):
        return jsonify({"error": "Invalid maze file"}), 400

    try:
        maze_path = os.path.join("mazes", maze)  # e.g., "mazes/maze1.txt"
        m = Maze(maze_path)
        image_filename = f"{maze.replace('.txt', '')}_original.png"
        output_path = os.path.join("static", image_filename)  # e.g., "static/maze1_original.png"

        m.output_image(output_path, show_solution=False)

        return send_file(output_path, mimetype='image/png')
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
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
