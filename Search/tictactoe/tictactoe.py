"""
Tic Tac Toe Player
"""
from copy import deepcopy
import math

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
    x = 0
    o = 0
    for row in board:
        for cell in row:
            if cell == "X":
                x += 1
            elif cell == "O":
                o += 1
    if o >= x:
        return X
    else:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    possibilities = set()
    for x, row in enumerate(board):
        for y, cell in enumerate(row):
            if cell is EMPTY:
                possibilities.add((x, y))
    return possibilities


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    i, j = action
    if board[i][j] is EMPTY:
        board1 = deepcopy(board)
        board1[i][j] = player(board)
        return board1
    else:
        raise Exception("Invalid Action")


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """

    """
    x - - | - x - | - - x
    x - - | - x - | - - x
    x - - | - x - | - - x
    """

    def vertical_winner(player_symbol):
        if (
                (board[0][0] == player_symbol and board[1][0] == player_symbol and board[2][0] == player_symbol) or
                (board[0][1] == player_symbol and board[1][1] == player_symbol and board[2][1] == player_symbol) or
                (board[0][2] == player_symbol and board[1][2] == player_symbol and board[2][2] == player_symbol)
        ):
            return True
        else:
            return False

    if vertical_winner(X):
        return X
    elif vertical_winner(O):
        return O

    """
    x x x | - - - | - - -
    - - - | x x x | - - -
    - - - | - - - | x x x
    """

    def horizontal_winner(player_symbol):
        if (
                (board[0][0] == player_symbol and board[0][1] == player_symbol and board[0][2] == player_symbol) or
                (board[1][0] == player_symbol and board[1][1] == player_symbol and board[1][2] == player_symbol) or
                (board[2][0] == player_symbol and board[2][1] == player_symbol and board[2][2] == player_symbol)
        ):
            return True
        else:
            return False

    if horizontal_winner(X):
        return X
    elif horizontal_winner(O):
        return O

    """
    x - - | - - x
    - x - | - x -
    - - x | x - -
    """

    def diagonally_winner(player_symbol):
        if (
                (board[0][0] == player_symbol and board[1][1] == player_symbol and board[2][2] == player_symbol) or
                (board[0][2] == player_symbol and board[1][1] == player_symbol and board[2][0] == player_symbol)
        ):
            return True
        else:
            return False

    if diagonally_winner(X):
        return X
    elif diagonally_winner(O):
        return O

    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """

    if winner(board) is not None:
        return True

    for row in board:
        for cell in row:
            if cell is EMPTY:
                return False

    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None
    elif player(board) == X:
        best_value = -1
        op_move = (1, 1)
        if op_move in actions(board):
            return op_move
        else:
            for action in actions(board):
                move_value = min_value(result(board, action))
                if winner(result(board, action)) == X:
                    return action
                if move_value == 1:
                    op_move = action
                    best_value = 1
                if move_value > best_value:
                    best_value = move_value
                    op_move = action
            return op_move
    elif player(board) == O:
        best_value = 1
        op_move = (1, 1)
        if op_move in actions(board):
            return op_move
        else:
            for action in actions(board):
                move_value = max_value(result(board, action))
                if move_value == -1:
                    return action
                elif move_value < best_value:
                    best_value = move_value
                    op_move = action
            return op_move


def max_value(state):
    if terminal(state):
        return utility(state)
    v = -math.inf
    for action in actions(state):
        v = max(v, min_value(result(state, action)))
        if v == 1:
            break
    return v


def min_value(state):
    if terminal(state):
        return utility(state)
    v = math.inf
    for action in actions(state):
        v = min(v, max_value(result(state, action)))
        if v == -1:
            break
    return v
