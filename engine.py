import copy
import main

"""
Responsible for storing all the information about the current state of the chess game.
Also will be responsible for determining the valid moves at the current state.
It will also keep a log of the moves that have been played.
"""


class GameState:
    def __init__(self):
        """
        Board is a list of 8 lists
        An unoccupied space on the board is represented with two dashes "--"
        A space with a piece has a logical name for the piece it represents - the first letter designates white or black
        The second character designates the type of piece B = bishop, K = king etc according to standard chess notation
        """
        self.board = [["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
                      ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
                      ["--", "--", "--", "--", "--", "--", "--", "--"],
                      ["--", "--", "--", "--", "--", "--", "--", "--"],
                      ["--", "--", "--", "--", "--", "--", "--", "--"],
                      ["--", "--", "--", "--", "--", "--", "--", "--"],
                      ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
                      ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.white_to_move = True
        self.move_log = []
        self.move_functions = {"P": self.get_pawn_moves, "R": self.get_rook_moves, "N": self.get_knight_moves,
                               "B": self.get_bishop_moves, "Q": self.get_queen_moves, "K": self.get_king_moves}
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        self.in_check = False
        self.pins = []
        self.checks = []
        self.checkmate = False
        self.stalemate = False
        self.en_passant_possible = ()  # coordinates of end square where en passant capture is possible
        self.en_passant_possible_log = [self.en_passant_possible]
        self.current_castling_rights = CastleRights(True, True, True, True)
        self.castle_rights_log = [CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                               self.current_castling_rights.wqs, self.current_castling_rights.bqs)]

    """
    Accepts a Move as a parameter and executes it
    """
    def make_move(self, move):
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)
        if move.piece_moved == "wK":
            self.white_king_location = (move.end_row, move.end_col)
        elif move.piece_moved == "bK":
            self.black_king_location = (move.end_row, move.end_col)
        self.white_to_move = not self.white_to_move

        # pawn promotion
        # TODO allow player to disable auto-queen
        if move.is_pawn_promotion:
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + "Q"

        # en passant
        if move.en_passant_move:
            self.board[move.start_row][move.end_col] = "--"  # capture the pawn

        # update en_passant_possible variable
        if move.piece_moved[1] == "P" and abs(move.start_row - move.end_row) == 2:
            self.en_passant_possible = ((move.start_row + move.end_row)//2, move.start_col)
        else:
            self.en_passant_possible = ()

        # update en passant log
        self.en_passant_possible_log.append(self.en_passant_possible)

        # castle move
        if move.is_castle_move:
            if move.end_col - move.start_col == 2:  # kingside castle
                self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][move.end_col + 1]  # move the rook
                self.board[move.end_row][move.end_col + 1] = "--"  # erase the old rook
            else:  # queenside castle
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 2]  # move the rook
                self.board[move.end_row][move.end_col - 2] = "--"  # erase the old rook

        # update castling rights whenever a rook or a king moves
        self.update_castle_rights(move)
        self.castle_rights_log.append(CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                                   self.current_castling_rights.wqs, self.current_castling_rights.bqs))

    """
    Undoes the last move made
    """
    def undo_move(self):
        if len(self.move_log) != 0:  # make sure there is a move to undo
            move = self.move_log.pop()  # delete the move with reference
            self.board[move.start_row][move.start_col] = move.piece_moved  # put the piece back where it was
            self.board[move.end_row][move.end_col] = move.piece_captured  # return the attacked square to original state
            if move.piece_moved == "wK":  # update the king position tuple if needed
                self.white_king_location = (move.start_row, move.start_col)
            elif move.piece_moved == "bK":
                self.black_king_location = (move.start_row, move.start_col)
            self.white_to_move = not self.white_to_move

            # undo en passant
            if move.en_passant_move:
                self.board[move.end_row][move.end_col] = "--"  # leave landing space blank
                self.board[move.start_row][move.end_col] = move.piece_captured

            # update en passant
            self.en_passant_possible_log.pop()
            self.en_passant_possible = self.en_passant_possible_log[-1]

            # undo castling rights
            self.castle_rights_log.pop()  # delete the updated castle rights since we are undoing that move
            self.current_castling_rights = copy.deepcopy(self.castle_rights_log[-1])  # set the castle rights to the previous state

            # undo castling
            if move.is_castle_move:
                if move.end_col - move.start_col == 2:  # kingside castle
                    self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 1]
                    self.board[move.end_row][move.end_col - 1] = "--"
                else:  # queenside castle
                    self.board[move.end_row][move.end_col - 2] = self.board[move.end_row][move.end_col + 1]
                    self.board[move.end_row][move.end_col + 1] = "--"

            # undo checkmate, stalemate since undoing a move reverses any of these
            self.checkmate = False
            self.stalemate = False


    """
    Update the castling rights given the move
    """
    def update_castle_rights(self, move):
        # if the king moves, castling is no longer possible
        if move.piece_moved == "wK":
            self.current_castling_rights.wks = False
            self.current_castling_rights.wqs = False
        elif move.piece_moved == "bK":
            self.current_castling_rights.bks = False
            self.current_castling_rights.bqs = False
        # if the rook moves, castling is not possible on that side anymore
        elif move.piece_moved == "wR":  # white rook
            if move.start_col == 0:  # queen side rook
                self.current_castling_rights.wqs = False
            elif move.start_col == 7:  # king size rook
                self.current_castling_rights.wks = False
        elif move.piece_moved == "bR":  # black rook
            if move.start_col == 0:  # queen side rook
                self.current_castling_rights.bqs = False
            elif move.start_col == 7:  # king side rook
                self.current_castling_rights.bks = False
        # if a rook is captured
        if move.piece_captured == "wR":
            if move.end_row == 7:
                if move.end_col == 0:
                    self.current_castling_rights.wqs = False
                elif move.end_col == 7:
                    self.current_castling_rights.wks = False
        elif move.piece_captured == "bR":
            if move.end_row == 0:
                if move.end_col == 0:
                    self.current_castling_rights.bqs = False
                elif move.end_col == 7:
                    self.current_castling_rights.bks = False

    """
    All moves considering checks
    """
    def get_valid_moves(self):
        moves = []
        self.in_check, self. pins, self.checks = self.get_pins_and_checks()
        temp_castle_rights = CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                          self.current_castling_rights.wqs, self.current_castling_rights.bqs)

        if self.white_to_move:
            king_row = self.white_king_location[0]
            king_col = self.white_king_location[1]
            self.get_castle_moves(self.white_king_location[0], self.white_king_location[1], moves, "w")
        else:
            king_row = self.black_king_location[0]
            king_col = self.black_king_location[1]
            self.get_castle_moves(self.black_king_location[0], self.black_king_location[1], moves, "b")
        if self.in_check:  # if in check
            if len(self.checks) == 1:  # if there's only one piece checking, you can block or capture
                moves = self.get_all_possible_moves()
                check = self.checks[0]  # get check info
                check_row = check[0]
                check_col = check[1]
                piece_checking = self.board[check_row][check_col]
                valid_squares = []  # list of valid squares pieces can move to
                # if the piece is a knight, you must capture the knight or move king
                if piece_checking[1] == "N":
                    valid_squares = [(check_row, check_col)]
                else:
                    for i in range(1, 8):
                        valid_square = (king_row + check[2] * i, king_col + check[3] * i)
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_row and valid_square[1] == check_col:  # you have reached the piece
                            break
                for i in range(len(moves) - 1, -1, -1):  # iterate backwards so we can delete without skipping
                    if moves[i].piece_moved[1] != "K":  # king doesn't move so it must be a block or capture
                        if not (moves[i].end_row, moves[i].end_col) in valid_squares:  # move doesn't block or capture
                            moves.remove(moves[i])
            else:  # double check => king must move
                self.get_king_moves(king_row, king_col, moves)
        else:  # not in check
            moves = self.get_all_possible_moves()

        if self.white_to_move:
            self.get_castle_moves(self.white_king_location[0], self.white_king_location[1], moves, "w")
        else:
            self.get_castle_moves(self.black_king_location[0], self.black_king_location[1], moves, "b")

        self.current_castling_rights = temp_castle_rights

        if len(moves) == 0:
            if self.in_check:
                self.checkmate = True
            else:
                self.stalemate = True
        return moves

    """
    Determines if the current player is in check
    """
    def in_check(self):
        if self.white_to_move:
            return self.square_under_attack(self.white_king_location[0], self.white_king_location[1])
        else:
            return self.square_under_attack(self.black_king_location[0], self.black_king_location[1])

    """
    Determines if a square is attacked by an enemy piece
    """
    def square_under_attack(self, row, col):
        self.white_to_move = not self.white_to_move  # pretend it's the opponent's turn
        opponent_moves = self.get_all_possible_moves()  # generate all their moves
        self.white_to_move = not self.white_to_move  # set the move back to our turn
        for move in opponent_moves:  # iterate through our list of opponent moves
            if move.end_row == row and move.end_col == col:  # check if the move attacks our square
                return True
        return False

    """
    All moves not considering checks
    """
    def get_all_possible_moves(self):
        moves = []
        #  traverse the board looking for pieces
        for row in range(len(self.board)):
            for col in range(len(self.board)):
                turn = self.board[row][col][0]
                # if you find a piece and it's their turn
                if (turn == 'w' and self.white_to_move) or (turn == 'b' and not self.white_to_move):
                    piece = self.board[row][col][1]  # get the piece type
                    self.move_functions[piece](row, col, moves)  # find all the possible moves for that piece
        return moves

    """
    Checks for pins and checks
    """
    def get_pins_and_checks(self):
        pins = []
        checks = []
        in_check = False
        if self.white_to_move:
            ally_color = "w"
            enemy_color = "b"
            start_row = self.white_king_location[0]
            start_col = self.white_king_location[1]
        else:
            ally_color = "b"
            enemy_color = "w"
            start_row = self.black_king_location[0]
            start_col = self.black_king_location[1]
        directions = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        for j in range(len(directions)):
            d = directions[j]
            possible_pin = ()  # reset possible pins
            for i in range(1, 8):
                end_row = start_row + d[0] * i
                end_col = start_col + d[1] * i
                if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == ally_color and end_piece[1] != "K":
                        if possible_pin == ():  # this is the first allied piece we have run into and could be pinned
                            possible_pin = (end_row, end_col, d[0], d[1])
                        else:  # this is the second allied piece in this direction and can't be pinned
                            break
                    elif end_piece[0] == enemy_color:
                        piece_type = end_piece[1]
                        # 5 possibilities
                        # 1. Piece is a rook and is orthogonal to king
                        # 2. Piece is a bishop and is diagonal to king
                        # 3. Piece is a pawn and is one square away diagonally
                        # 4. Piece is a queen and is any direction from king
                        # 5. Piece is a king and is one square away in any direction
                        if (0 <= j <= 3 and piece_type == "R") or \
                           (4 <= j <= 7 and piece_type == "B") or \
                           (i == 1 and piece_type == "P" and ((enemy_color == "w" and 6 <= j <= 7) or
                                                              (enemy_color == "b" and 4 <= j <= 5))) or \
                           (piece_type == "Q") or (i == 1 and piece_type == "K"):
                            if possible_pin == ():  # there is no ally piece blocking check
                                in_check = True
                                checks.append((end_row, end_col, d[0], d[1]))
                                break
                            else:  # piece blocking check
                                pins.append(possible_pin)
                                break
                        else:  # enemy piece not giving check
                            break
                else:  # off board
                    break
        # check for knight checks
        knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        for move in knight_moves:
            end_row = start_row + move[0]
            end_col = start_col + move[1]
            if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy_color and end_piece[1] == "N":
                    in_check = True
                    checks.append((end_row, end_col, d[0], d[1]))
        return in_check, pins, checks

    """
    Get all legal pawn moves located at a specific row and column
    """
    # TODO allow pawn to promote to something other than queen
    def get_pawn_moves(self, row, col, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.white_to_move:  # white's turn => pawns move up the board
            king_row, king_col = self.white_king_location
            # check if there's a piece blocking the pawn from moving one square forward
            if self.board[row - 1][col] == "--":
                if not piece_pinned or pin_direction == (-1, 0):
                    moves.append(Move((row, col), (row - 1, col), self.board))
                    # if the pawn is on it's starting row it can move two squares forward if no pieces are blocking it
                    if row == 6 and self.board[row - 2][col] == "--":
                        moves.append(Move((row, col), (row - 2, col), self.board))
            if col > 0:  # we are not on the left edge of the board
                if self.board[row - 1][col - 1][0] == "b":  # there is a black piece to the left
                    if not piece_pinned or pin_direction == (-1, -1):  # the pawn is not pinned or it is capturing the pinner
                        moves.append(Move((row, col), (row - 1, col - 1), self.board))
                elif (row - 1, col - 1) == self.en_passant_possible:  # check if en passant is possible
                    attacking_piece = blocking_piece = False
                    if king_row == row:
                        if king_col < col:  # king col is less than col of pawn
                            # inside is between king and pawn, outside is between pawn and board
                            inside_range = range(king_col + 1, col - 1)
                            outside_range = range(col + 1, 8)
                        else:  # king is to the right of the pawn
                            inside_range = range(king_col - 1, col, -1)
                            outside_range = range(col - 2, -1, -1)
                        for i in inside_range:
                            if self.board[row][i] != "--":  # some other piece besides en-passant pawn is blocking
                                blocking_piece = True
                        for i in outside_range:
                            square = self.board[row][i]
                            if square[0] == "b" and (square[1] == "R" or square[1] == "Q"):
                                attacking_piece = True
                            elif square != "--":
                                blocking_piece = True
                    if not attacking_piece or blocking_piece:
                        moves.append(Move((row, col), (row - 1, col - 1), self.board, en_passant_move=True))
            if col < 7:  # we are not on the right edge of the board
                if self.board[row - 1][col + 1][0] == "b":  # there is a black piece to the right
                    if not piece_pinned or pin_direction == (-1, 1):  # pawn is not pinned or it is capturing the pinner
                        moves.append(Move((row, col), (row - 1, col + 1), self.board))
                elif (row - 1, col + 1) == self.en_passant_possible:  # check if en passant is possible
                    attacking_piece = blocking_piece = False
                    if king_row == row:
                        if king_col < col:  # king col is less than col of pawn
                            # inside is between king and pawn, outside is between pawn and board
                            inside_range = range(king_col + 1, col)
                            outside_range = range(col + 2, 8)
                        else:  # king is to the right of the pawn
                            inside_range = range(king_col - 1, col + 1, -1)
                            outside_range = range(col - 1, -1, -1)
                        for i in inside_range:
                            if self.board[row][i] != "--":  # some other piece besides en-passant pawn is blocking
                                blocking_piece = True
                        for i in outside_range:
                            square = self.board[row][i]
                            if square[0] == "b" and (square[1] == "R" or square[1] == "Q"):
                                attacking_piece = True
                            elif square != "--":
                                blocking_piece = True
                    if not attacking_piece or blocking_piece:
                        moves.append(Move((row, col), (row - 1, col + 1), self.board, en_passant_move=True))

        elif not self.white_to_move:  # black's turn => pawns move down the board
            king_row, king_col = self.black_king_location
            # check if there's a piece blocking the pawn from moving one square forward
            if self.board[row + 1][col] == "--":
                if not piece_pinned or pin_direction == (1, 0):
                    moves.append(Move((row, col), (row + 1, col), self.board))
                    # if the pawn is on it's starting row it can move two squares forward if no pieces are blocking it
                    if row == 1 and self.board[row + 2][col] == "--":
                        moves.append(Move((row, col), (row + 2, col), self.board))
            if col > 0:  # we are not on the left edge of the board
                if self.board[row + 1][col - 1][0] == "w":  # there is a white piece to the left
                    if not piece_pinned or pin_direction == (1, -1):  # the pawn is not pinned or it capturing the pinner
                        moves.append(Move((row, col), (row + 1, col - 1), self.board))
                elif (row + 1, col - 1) == self.en_passant_possible:  # check if en passant is possible
                    attacking_piece = blocking_piece = False
                    if king_row == row:
                        if king_col < col:  # king col is less than col of pawn
                            # inside is between king and pawn, outside is between pawn and board
                            inside_range = range(king_col + 1, col - 1)
                            outside_range = range(col + 1, 8)
                        else:  # king is to the right of the pawn
                            inside_range = range(king_col - 1, col, -1)
                            outside_range = range(col - 2, -1, -1)
                        for i in inside_range:
                            if self.board[row][i] != "--":  # some other piece besides en-passant pawn is blocking
                                blocking_piece = True
                        for i in outside_range:
                            square = self.board[row][i]
                            if square[0] == "w" and (square[1] == "R" or square[1] == "Q"):
                                attacking_piece = True
                            elif square != "--":
                                blocking_piece = True
                    if not attacking_piece or blocking_piece:
                        moves.append(Move((row, col), (row + 1, col - 1), self.board, en_passant_move=True))
            if col < 7:  # we are not on the right edge of the board
                if self.board[row + 1][col + 1][0] == "w":  # there is a white piece to the right
                    if not piece_pinned or pin_direction == (1, 1):  # the pawn is not pinned or it is capturing the pinner
                        moves.append(Move((row, col), (row + 1, col + 1), self.board))
                elif (row + 1, col + 1) == self.en_passant_possible:  # check if en passant is possible
                    attacking_piece = blocking_piece = False
                    if king_row == row:
                        if king_col < col:  # king col is less than col of pawn
                            # inside is between king and pawn, outside is between pawn and board
                            inside_range = range(king_col + 1, col)
                            outside_range = range(col + 2, 8)
                        else:  # king is to the right of the pawn
                            inside_range = range(king_col - 1, col + 1, -1)
                            outside_range = range(col - 1, -1, -1)
                        for i in inside_range:
                            if self.board[row][i] != "--":  # some other piece besides en-passant pawn is blocking
                                blocking_piece = True
                        for i in outside_range:
                            square = self.board[row][i]
                            if square[0] == "w" and (square[1] == "R" or square[1] == "Q"):
                                attacking_piece = True
                            elif square != "--":
                                blocking_piece = True
                    if not attacking_piece or blocking_piece:
                        moves.append(Move((row, col), (row + 1, col + 1), self.board, en_passant_move=True))

    """
    Get all legal rook moves located at a specific row and column
    """
    # This function works by looking in a direction until it finds a piece in the way, adding moves along the way
    def get_rook_moves(self, row, col, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if self.board[row][col][1] != "Q":  # we don't want to remove moves from the list for queens
                    self.pins.remove(self.pins[i])
                break

        rook_moves = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        opponent_color = "b" if self.white_to_move else "w"
        for move in rook_moves:
            for i in range(1, 8):
                candidate_row = row + move[0] * i
                candidate_col = col + move[1] * i
                if 0 <= candidate_row <= 7 and 0 <= candidate_col <= 7:
                    # If the piece is not pinned, or we are moving in the direction of the pin, or in the opposite
                    # direction of the pin, it is a valid move
                    if not piece_pinned or pin_direction == move or pin_direction == (-move[0], -move[1]):
                        if self.board[candidate_row][candidate_col] == "--":  # move is to an empty square
                            moves.append(Move((row, col), (candidate_row, candidate_col), self.board))
                        elif self.board[candidate_row][candidate_col][0] == opponent_color:  # capture
                            moves.append(Move((row, col), (candidate_row, candidate_col), self.board))
                            break
                        else:  # friendly piece
                            break
                else:  # not on board
                    break

    """
    Get all legal bishop moves located at a specific row and column
    """
    def get_bishop_moves(self, row, col, moves):
        #  same idea as rook moves: pick a direction and add moves until you hit a piece
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])

        opponent_color = "b" if self.white_to_move else "w"
        bishop_moves = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for move in bishop_moves:
            for i in range(1, 8):
                candidate_row = row + move[0] * i
                candidate_col = col + move[1] * i
                if 0 <= candidate_row <= 7 and 0 <= candidate_col <= 7:  # check that square is on the board
                    # If the piece is not pinned, or the piece wants to move either in the direction of the pin,
                    # or the opposite direction of the pin, it is a valid move
                    if not piece_pinned or pin_direction == move or pin_direction == (-move[0], -move[1]):
                        if self.board[candidate_row][candidate_col] == "--":  # move to an empty square
                            moves.append(Move((row, col), (candidate_row, candidate_col), self.board))
                        elif self.board[candidate_row][candidate_col][0] == opponent_color:  # capture
                            moves.append(Move((row, col), (candidate_row, candidate_col), self.board))
                            break
                        else:  # ally piece
                            break
                else:  # off the board
                    break

    """
    Get all legal knight moves located at a specific row and column
    """
    def get_knight_moves(self, row, col, moves):
        # we can simply test all eight possible knight moves for legality
        # tuples of (row, column) give every possible knight move from a current position
        piece_pinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                self.pins.remove(self.pins[i])
                break

        knight_moves = [(1, 2), (-1, 2), (1, -2), (2, 1), (-2, 1), (2, -1), (-2, -1), (-1, -2)]
        ally_color = "w" if self.white_to_move else "b"
        for move in knight_moves:
            candidate_row = row + move[0]
            candidate_col = col + move[1]
            if 0 <= candidate_row <= 7 and 0 <= candidate_col <= 7:  # make sure the square is on the board
                if not piece_pinned:
                    if self.board[move[0] + row][move[1] + col][0] != ally_color:
                        moves.append(Move((row, col), (candidate_row, candidate_col), self.board))

    """
    Get all legal queen moves located at a specific row and column
    """
    def get_queen_moves(self, row, col, moves):
        # The idea for queen moves is to combine the rook and bishop moves
        self.get_bishop_moves(row, col, moves)
        self.get_rook_moves(row, col, moves)

    """
    Get all legal king moves located at a specific row and column
    """
    def get_king_moves(self, row, col, moves):
        row_moves = (-1, -1, -1, 0, 0, 1, 1, 1)
        col_moves = (-1, 0, 1, -1, 1, -1, 0, 1)
        ally_color = "w" if self.white_to_move else "b"
        for i in range(8):
            candidate_row = row + row_moves[i]
            candidate_col = col + col_moves[i]
            if 0 <= candidate_row <= 7 and 0 <= candidate_col <= 7:  # make sure the square is on the board
                if self.board[candidate_row][candidate_col][0] != ally_color:
                    # the idea here is to make the candidate move and see if it results in check
                    if ally_color == "w":
                        self.white_king_location = (candidate_row, candidate_col)
                    else:
                        self.black_king_location = (candidate_row, candidate_col)
                    in_check, pins, checks = self.get_pins_and_checks()

                    if not in_check:  # add to valid moves list
                        moves.append(Move((row, col), (candidate_row, candidate_col), self.board))
                    if ally_color == "w":  # move the king back
                        self.white_king_location = (row, col)
                    else:
                        self.black_king_location = (row, col)

    """
    Get castling moves and add them to move list
    """
    def get_castle_moves(self, row, col, moves, ally_color):
        if self.square_under_attack(row, col):  # can't castle if in check
            return
        if (self.white_to_move and self.current_castling_rights.wks) or \
                (not self.white_to_move and self.current_castling_rights.bks):
            self.get_kingside_castle_moves(row, col, moves, ally_color)
        if (self.white_to_move and self.current_castling_rights.wqs) or \
                (not self.white_to_move and self.current_castling_rights.bqs):
            self.get_queenside_castle_moves(row, col, moves, ally_color)

    def get_kingside_castle_moves(self, row, col, moves, ally_color):
        if self.board[row][col + 1] == "--" and self.board[row][col + 2] == "--":
            if not self.square_under_attack(row, col + 1) and not self.square_under_attack(row, col + 2):
                moves.append(Move((row, col), (row, col + 2), self.board, is_castle_move=True))

    def get_queenside_castle_moves(self, row, col, moves, ally_color):
        if self.board[row][col - 1] == "--" and self.board[row][col - 2] == "--" and self.board[row][col - 3] == "--":
            if not self.square_under_attack(row, col - 1) and not self.square_under_attack(row, col - 2) and not self.square_under_attack(row, col - 3):
                moves.append(Move((row, col), (row, col - 2), self.board, is_castle_move=True))


class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move:
    # maps keys to values
    # key : value
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                     "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3,
                     "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_square, end_square, board, en_passant_move=False, is_castle_move=False, is_check=False, is_checkmate=False):
        self.start_row = start_square[0]
        self.start_col = start_square[1]
        self.end_row = end_square[0]
        self.end_col = end_square[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        # pawn promotion
        self.is_pawn_promotion = (self.piece_moved == "wP" and self.end_row == 0) or (self.piece_moved == "bP" and self.end_row == 7)
        # en passant
        self.en_passant_move = en_passant_move
        if self.en_passant_move:
            self.piece_captured = "wP" if self.piece_moved == "bP" else "bP"
        self.is_capture = self.piece_captured != "--"
        # castle
        self.is_castle_move = is_castle_move
        self.move_ID = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col
        self.is_check = False
        self.is_checkmate = False

    """
    Overriding the equals method
    """
    def __eq__(self, other):
        if isinstance(other, Move):
            return other.move_ID == self.move_ID
        return False

    def get_chess_notation(self):
        # TODO check/checkmate
        # TODO multiple possible pieces moving to destination
        if self.piece_moved[-1] != "P":  # if the piece moved is not a pawn
            if self.piece_captured != "--":  # if we captured a piece
                return self.piece_moved[-1] + "x" + self.get_rank_file(self.end_row, self.end_col)  # e.g. Qxf5
            else:  # we did not capture a piece
                return self.piece_moved[-1] + self.get_rank_file(self.end_row, self.end_col)  # e.g. Qf5
        elif self.piece_captured != "--":  # if we moved a pawn and captured a piece
            return self.get_rank_file(self.start_row, self.start_col)[0] + "x" + self.get_rank_file(self.end_row, self.end_col)  # e.g. exf5
        else:  # if we moved a pawn and did not capture a piece
            return self.get_rank_file(self.end_row, self.end_col)  # e.g. d4

    def get_rank_file(self, row, col):
        return self.cols_to_files[col] + self.rows_to_ranks[row]

    # overriding the str() function
    def __str__(self):
        # castle move
        if self.is_castle_move:
            return "O-O" if self.end_col == 6 else "O-O-O"

        end_square = self.get_rank_file(self.end_row, self.end_col)
        # pawn moves
        if self.piece_moved[1] == "P":
            if self.is_capture:
                if self.is_checkmate:
                    return self.cols_to_files[self.start_col] + "x" + end_square + "#"
                elif self.is_check:
                    return self.cols_to_files[self.start_col] + "x" + end_square + "!"
                else:
                    return self.cols_to_files[self.start_col] + "x" + end_square
            else:
                if self.is_checkmate:
                    return end_square + "#"
                elif self.is_check:
                    return end_square + "!"
                else:
                    return end_square

        # piece moves
        move_string = self.piece_moved[1]
        if self.is_capture:
            move_string += "x"

        if self.is_checkmate:
            return move_string + end_square + "#"

        elif self.is_check:
            return move_string + end_square + "#"

        else:
            return move_string + end_square
