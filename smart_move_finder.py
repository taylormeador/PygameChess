import random

piece_values = {"Q": 10, "R": 5, "B": 3, "N": 3, "P": 1, "K": 0}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 3


"""
Returns a random move
"""


def find_random_move(valid_moves):
    return valid_moves[random.randint(0, len(valid_moves) - 1)]


"""
Find the best move given the material on the board. Non recursive minmax
"""


def find_best_move(gs, valid_moves):
    opponent_min_max_score = CHECKMATE
    best_player_move = None
    turn_multiplier = 1 if gs.white_to_move else -1
    for player_move in valid_moves:
        gs.make_move(player_move)
        opponent_moves = gs.get_valid_moves()
        opponent_max_score = -CHECKMATE
        for opponent_move in opponent_moves:  # find the best move for the opponent
            gs.make_move(opponent_move)
            if gs.checkmate:
                score = CHECKMATE
            elif gs.stalemate:
                score = STALEMATE
            else:
                score = -turn_multiplier * score_material(gs.board)
            if score > opponent_max_score:
                opponent_max_score = score
            gs.undo_move()
        if opponent_max_score < opponent_min_max_score:  # find the player best move based on opponent's best response
            opponent_min_max_score = opponent_max_score
            best_player_move = player_move
        gs.undo_move()
    return best_player_move


"""
Helper method to make the first recursive call of minmax
"""

def find_best_move_min_max(gs, valid_moves):
    global next_move
    next_move = None
    find_move_min_max(gs, valid_moves, DEPTH, gs.white_to_move)
    return next_move


"""
Recursive min max
"""


def find_move_min_max(gs, valid_moves, depth, white_to_move):
    global next_move
    if depth == 0:
        return score_material(gs.board)

    if white_to_move:
        max_score = -CHECKMATE
        for move in valid_moves:
            gs.make_move(move)
            next_moves = gs.get_valid_moves()
            score = find_move_min_max(gs, next_moves, depth - 1, False)
            if score > max_score:
                max_score = score
                if depth == DEPTH:
                    next_move = move
            gs.undo_move()
        return max_score

    else:
        min_score = CHECKMATE
        for move in valid_moves:
            gs.make_move(move)
            next_moves = gs.get_valid_moves()
            score = find_move_min_max(gs, next_moves, depth - 1, True)
            if score < min_score:
                min_score = score
                if depth == DEPTH:
                    next_move = move
            gs.undo_move()
        return min_score


"""
Score the position. Positive score is good for white, negative is good for black
"""


def score_board(gs):
    if gs.checkmate:
        if gs.white_to_move:
            return CHECKMATE  # black wins
        else:
            return CHECKMATE  # white wins
    elif gs.stalemate:
        return STALEMATE

    score = 0
    for row in gs.board:
        for square in row:
            if square[0] == "w":
                score += piece_values[square[1]]
            elif square[0] == "b":
                score -= piece_values[square[1]]

    return score


"""
Count the material
"""


def score_material(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == "w":
                score += piece_values[square[1]]
            elif square[0] == "b":
                score -= piece_values[square[1]]

    return score
