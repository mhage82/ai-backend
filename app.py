from flask import (
    Flask,
    request,
    jsonify,
    send_from_directory,
    send_file,
)
from flask_cors import CORS
from flask_sock import Sock

import os
import threading


# ---------------------------------------------------------------------------
# Existing project imports
# ---------------------------------------------------------------------------

# Import from search folder
from search.maze_solver import Maze
from search.maze_stack import solve_stack
from search.maze_queue import solve_queue

from ttt.ttt_logic import (
    initial_state,
    player,
    actions,
    result,
    winner,
    terminal,
)


# ---------------------------------------------------------------------------
# Flask application
# ---------------------------------------------------------------------------

app = Flask(__name__)

CORS(app)

sock = Sock(app)


# Ensure static directory exists
os.makedirs(
    "static",
    exist_ok=True,
)


# ---------------------------------------------------------------------------
# KVM connection state
# ---------------------------------------------------------------------------

# Holds the currently-connected Raspberry Pi WebSocket.
#
# None means the Pi is offline.
pi_connection = None


# Flask may handle multiple requests concurrently, so protect access
# to pi_connection.
pi_connection_lock = threading.Lock()


# ---------------------------------------------------------------------------
# Existing Maze API
# ---------------------------------------------------------------------------

@app.route("/maze-image/<maze>")
def maze_image(maze):
    if not maze.endswith(".txt"):
        return jsonify({
            "error": "Invalid maze file"
        }), 400

    try:
        maze_path = os.path.join(
            "search",
            "mazes",
            maze,
        )

        m = Maze(maze_path)

        image_filename = (
            f"{maze.replace('.txt', '')}_original.png"
        )

        output_path = os.path.join(
            "static",
            image_filename,
        )

        m.output_image(
            output_path,
            show_solution=False,
        )

        return send_file(
            output_path,
            mimetype="image/png",
        )

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


@app.route("/solve", methods=["POST"])
def solve():
    data = request.get_json()

    maze_file = data.get("maze")
    algo = data.get("algorithm")

    full_path = os.path.join(
        "search",
        "mazes",
        maze_file,
    )

    if not os.path.exists(full_path):
        return jsonify({
            "error": "Maze file not found."
        }), 404

    try:
        if algo == "stack":
            result_data = solve_stack(
                full_path
            )

        elif algo == "queue":
            result_data = solve_queue(
                full_path
            )

        else:
            return jsonify({
                "error": "Unknown algorithm."
            }), 400

        return jsonify(
            result_data
        )

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


@app.route("/static/<filename>")
def static_file(filename):
    return send_from_directory(
        "static",
        filename,
    )


# ---------------------------------------------------------------------------
# Existing Tic-Tac-Toe API
# ---------------------------------------------------------------------------

@app.route("/ttt/start", methods=["GET"])
def ttt_start():
    return jsonify({
        "board": initial_state()
    })


@app.route("/ttt/move", methods=["POST"])
def ttt_move():
    from ttt.ttt_logic import minimax

    data = request.get_json()

    board = data.get("board")
    move = data.get("move")

    if board is None or move is None:
        return jsonify({
            "error": "Missing board or move."
        }), 400

    try:
        # Apply player's move as X.
        new_board = result(
            board,
            tuple(move),
            forced_player="X",
        )

        if terminal(new_board):
            return jsonify({
                "board": new_board,
                "next_player": None,
                "winner": winner(new_board),
                "game_over": True,
            })

        # AI move as O.
        ai_move = minimax(
            new_board
        )

        if ai_move is not None:
            new_board = result(
                new_board,
                ai_move,
                forced_player="O",
            )

        return jsonify({
            "board": new_board,
            "next_player": (
                None
                if terminal(new_board)
                else player(new_board)
            ),
            "winner": winner(new_board),
            "game_over": terminal(new_board),
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


# ---------------------------------------------------------------------------
# KVM HTTP API
# ---------------------------------------------------------------------------

@app.route("/kvm/status", methods=["GET"])
def kvm_status():
    """
    Returns whether the Raspberry Pi currently has an active
    WebSocket connection to this backend.
    """

    with pi_connection_lock:
        connected = (
            pi_connection is not None
        )

    return jsonify({
        "pi_connected": connected
    })


# ---------------------------------------------------------------------------
# Raspberry Pi KVM WebSocket
# ---------------------------------------------------------------------------

@sock.route("/ws/kvm/pi")
def kvm_pi_socket(ws):
    """
    Persistent WebSocket connection used by the Raspberry Pi.

    The Pi connects OUTBOUND to this endpoint.

    Authentication is performed with:

        X-KVM-Token: <secret>

    The expected secret is stored in the environment variable:

        KVM_PI_TOKEN

    Nothing secret is committed to Git.
    """

    global pi_connection


    # ---------------------------------------------------------------
    # Authentication
    # ---------------------------------------------------------------

    expected_token = os.environ.get(
        "KVM_PI_TOKEN"
    )

    provided_token = request.headers.get(
        "X-KVM-Token"
    )


    if not expected_token:
        print(
            "[KVM] ERROR: "
            "KVM_PI_TOKEN is not configured."
        )

        ws.close()

        return


    if provided_token != expected_token:
        print(
            "[KVM] Rejected Raspberry Pi connection: "
            "invalid token."
        )

        ws.close()

        return


    # ---------------------------------------------------------------
    # Register Pi connection
    # ---------------------------------------------------------------

    with pi_connection_lock:

        # If another Pi connection somehow already exists,
        # close the old one before replacing it.
        old_connection = pi_connection

        pi_connection = ws


    if (
        old_connection is not None
        and old_connection is not ws
    ):
        try:
            old_connection.close()

        except Exception:
            pass


    print(
        "[KVM] Raspberry Pi connected."
    )


    # ---------------------------------------------------------------
    # Receive loop
    # ---------------------------------------------------------------

    try:
        while True:

            message = ws.receive()

            if message is None:
                break


            # For now we simply log messages coming from the Pi.
            #
            # Later this will carry:
            #
            #   heartbeat
            #   HID acknowledgements
            #   connection state
            #   errors
            #
            print(
                f"[KVM] Pi -> Server: {message}"
            )


    except Exception as exc:
        print(
            "[KVM] Raspberry Pi WebSocket error: "
            f"{exc}"
        )


    # ---------------------------------------------------------------
    # Disconnect cleanup
    # ---------------------------------------------------------------

    finally:

        with pi_connection_lock:

            # Only clear it if THIS socket is still the active
            # Pi connection.
            if pi_connection is ws:
                pi_connection = None


        print(
            "[KVM] Raspberry Pi disconnected."
        )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            "10000",
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
    )