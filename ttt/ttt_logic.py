import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    x_played = 0
    o_played = 0
    for row in board:
        for square in row:
            if square == X:
                x_played += 1
            if square == O:
                o_played += 1
    if x_played == o_played:
        return X          
    elif x_played > o_played:
        return O
    else:
        raise("O played out of turn")


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    possible_actions = []
    for row_index, row in enumerate(board):
        for col_index, square in enumerate(row):
            if square is None:
                possible_actions.append((row_index, col_index))
    return possible_actions

def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    temp_board = copy.deepcopy(board)
    i, j = action
    temp_board[i][j] = player(board)
    return temp_board


def winner(board):
    """
    Returns the winner of the game if there is one.
    """
    # Rows and columns
    for i in range(3):
        if board[i][0] is not None and board[i][0] == board[i][1] == board[i][2]:
            return board[i][0]
        if board[0][i] is not None and board[0][i] == board[1][i] == board[2][i]:
            return board[0][i]
    # Diagonals
    if board[0][0] is not None and board[0][0] == board[1][1] == board[2][2]:
        return board[0][0]
    if board[0][2] is not None and board[0][2] == board[1][1] == board[2][0]:
        return board[0][2]
    return None

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    w = winner(board)
    if w in (X,O):
        return True
    else:
        for row in board:
            for square in row:
                if square is None:
                    return False
    return True

def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if terminal(board):
        w = winner(board)
        if w == X:
            return 1
        elif w == O:
            return -1
        else:
            return 0
    else:
        raise("Game is not done yet !!!")

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None

    current_player = player(board)

    def max_value(state):
        if terminal(state):
            return utility(state), None  # ✅ Return tuple
        v = float('-inf')
        best_move = None
        for action in actions(state):
            min_result, _ = min_value(result(state, action))
            if min_result > v:
                v = min_result
                best_move = action
        return v, best_move

    def min_value(state):
        if terminal(state):
            return utility(state), None  # ✅ Return tuple
        v = float('inf')
        best_move = None
        for action in actions(state):
            max_result, _ = max_value(result(state, action))
            if max_result < v:
                v = max_result
                best_move = action
        return v, best_move

    if current_player == X:
        _, move = max_value(board)
    else:
        _, move = min_value(board)

    return move
# board = [
#     ['O', 'O', 'X'],
#     ['O', 'X', 'X'],
#     [None, X, None]
# ]

# best_move = minimax(board)
# print("Best move for current player:{}".format(player(board)), best_move)
# print(result([[EMPTY,EMPTY,EMPTY],[EMPTY,EMPTY,EMPTY],[EMPTY,EMPTY,EMPTY]], (1,2)))
# X wins by row
# game1 = [
#     ['X', 'X', 'X'],
#     ['O', 'O', None],
#     [None, None, None]
# ]

# # O wins by column
# game2 = [
#     ['O', 'X', 'X'],
#     ['O', 'X', None],
#     ['O', None, None]
# ]

# # X wins by main diagonal
# game3 = [
#     ['X', 'O', None],
#     [None, 'X', 'O'],
#     [None, None, 'X']
# ]

# # No winner
# game4 = [
#     ['X', 'O', 'X'],
#     ['X', 'O', 'O'],
#     ['O', 'X', 'X']
# ]

# print(winner(game1))  # X
# print(winner(game2))  # O
# print(winner(game3))  # X
# print(winner(game4))  # None

# # Test 1: X wins
# board1 = [
#     ['X', 'X', 'X'],
#     ['O', 'O', None],
#     [None, None, None]
# ]
# print("Game Over (X wins):", terminal(board1))  # True

# # Test 2: O wins diagonally
# board2 = [
#     ['O', 'X', 'X'],
#     ['X', 'O', None],
#     ['X', None, 'O']
# ]
# print("Game Over (O wins):", terminal(board2))  # True

# # Test 3: Draw (board full, no winner)
# board3 = [
#     ['X', 'O', 'X'],
#     ['X', 'O', 'O'],
#     ['O', 'X', 'X']
# ]
# print("Game Over (Draw):", terminal(board3))  # True

# # Test 4: Still playing (empty cells, no winner)
# board4 = [
#     ['X', 'O', 'X'],
#     ['X', None, 'O'],
#     ['O', 'X', None]
# ]
# print("Game Over (Still playing):", terminal(board4))  # False

# # Test 5: Empty board
# board5 = [
#     [None, None, None],
#     [None, None, None],
#     [None, None, None]
# ]
# print("Game Over (Empty board):", terminal(board5))  # False
