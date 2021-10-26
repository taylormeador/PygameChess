import random
import datetime

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
Helper method to make the first recursive call of minmax
"""


def find_best_move(gs, valid_moves, return_queue):
    global next_move, counter
    next_move = None
    random.shuffle(valid_moves)  # to allow for variation in games with AI
    counter = 0
    begin_time = datetime.datetime.now()
    find_move_nega_max_alpha_beta(gs, valid_moves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.white_to_move else -1)
    execution_time = datetime.datetime.now() - begin_time
    print()
    print("# of moves evaluated: ",  counter)
    print("Time elapsed: ", execution_time)
    return_queue.put(next_move)


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


def find_move_nega_max(gs, valid_moves, depth, turn_multiplier):
    global next_move
    if depth == 0:
        return turn_multiplier * score_board(gs)

    max_score = -CHECKMATE
    for move in valid_moves:
        gs.make_move(move)
        next_moves = gs.get_valid_moves()
        score = -1 * find_move_nega_max(gs, next_moves, depth - 1, -turn_multiplier)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
        gs.undo_move()
    return max_score


def find_move_nega_max_alpha_beta(gs, valid_moves, depth, alpha, beta, turn_multiplier):
    global next_move, counter
    counter += 1
    if depth == 0:
        return turn_multiplier * score_board(gs)

    # TODO move ordering - implement method here that orders moves best to worst

    max_score = -CHECKMATE
    for move in valid_moves:
        gs.make_move(move)
        next_moves = gs.get_valid_moves()
        score = -find_move_nega_max_alpha_beta(gs, next_moves, depth - 1, -beta, -alpha, -turn_multiplier)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
        gs.undo_move()
        # pruning
        if max_score > alpha:
            alpha = max_score
        if alpha >= beta:
            break
    return max_score


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
