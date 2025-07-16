from .maze_solver import Maze

def solve_stack(filename):
    m = Maze(filename, use_stack=True)
    m.solve()
    m.output_image("static/maze.png", show_explored=True)
    return {
        "states_explored": m.num_explored,
        "text": m.as_text(),
        "image": "/static/maze.png"
    }
