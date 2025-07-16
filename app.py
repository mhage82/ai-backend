from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import os

# Import from search folder
from search.maze_solver import Maze
from search.maze_stack import solve_stack
from search.maze_queue import solve_queue

app = Flask(__name__)
CORS(app)

# Ensure static directory exists
os.makedirs("static", exist_ok=True)

@app.route("/maze-image/<maze>")
def maze_image(maze):
    if not maze.endswith(".txt"):
        return jsonify({"error": "Invalid maze file"}), 400

    try:
        maze_path = os.path.join("search", "mazes", maze)  #Updated for nested folder
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
    full_path = os.path.join("search", "mazes", maze_file)  # Updated for nested folder

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

@app.route("/ttt/start", methods=["GET"])
def ttt_start():
    return jsonify({"board": initial_state()})

@app.route("/ttt/move", methods=["POST"])
def ttt_move():
    data = request.get_json()
    board = data.get("board")
    move = data.get("move")  # e.g. [0, 2]
    if board is None or move is None:
        return jsonify({"error": "Missing board or move."}), 400
    try:
        new_board = result(board, tuple(move))
        current_player = player(new_board)
        game_over = terminal(new_board)
        win = winner(new_board)
        return jsonify({
            "board": new_board,
            "next_player": None if game_over else current_player,
            "winner": win,
            "game_over": game_over
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
