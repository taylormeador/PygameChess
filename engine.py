"""
Responsible for storing all the information about the current state of the chess game.
Also will be responsible for determining the valid moves at the current state.
It will also keep a log of the moves that have been played.
"""


class GameState:
    def __init__(self):
        """
        Board is a list of 8 lists
        An unoccupied space on the board is represented with two dashes
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
        self.pgn = []
        self.move_functions = {"P": self.get_pawn_moves, "R": self.get_rook_moves, "N": self.get_knight_moves, "B": self.get_bishop_moves, "Q": self.get_queen_moves, "K": self.get_king_moves}

    """
    Accepts a Move as a parameter and executes it (excepting castling, pawn promotion, and en passant)
    """
    def make_move(self, move):
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)
        self.pgn.append(move.get_chess_notation())
        self.white_to_move = not self.white_to_move

    """
    Undoes the last move made
    """
    def undo_move(self):
        if len(self.move_log) != 0:  # make sure there is a move to undo
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            del self.pgn[-1]
            self.white_to_move = not self.white_to_move

    """
    All moves considering checks
    """
    def get_valid_moves(self):
        return self.get_all_possible_moves()

    """
    All moves not considering checks
    """
    def get_all_possible_moves(self):
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board)):
                turn = self.board[row][col][0]
                if (turn == 'w' and self.white_to_move) or (turn == 'b' and not self.white_to_move):
                    piece = self.board[row][col][1]
                    self.move_functions[piece](row, col, moves)
        return moves

    """
    Get all legal pawn moves located at a specific row and column
    """
    def get_pawn_moves(self, row, col, moves):
        if self.white_to_move:  # white's turn => pawns move up the board
            # check if there's a piece blocking the pawn from moving one square forward
            if self.board[row - 1][col] == "--":
                moves.append(Move((row, col), (row - 1, col), self.board))
                # if the pawn is on it's starting row it can move two squares forward if no pieces are blocking it
                if row == 6 and self.board[row - 2][col] == "--":
                    moves.append(Move((row, col), (row - 2, col), self.board))
            if col > 0 and self.board[row - 1][col - 1][0] == "b":  # there is a black piece to the left
                moves.append(Move((row, col), (row - 1, col - 1), self.board))
            if col < 7 and self.board[row - 1][col + 1][0] == "b":  # there is a black piece to the right
                moves.append(Move((row, col), (row - 1, col + 1), self.board))
        elif not self.white_to_move:  # black's turn => pawns move down the board
            # check if there's a piece blocking the pawn from moving one square forward
            if self.board[row + 1][col] == "--":
                moves.append(Move((row, col), (row + 1, col), self.board))
                # if the pawn is on it's starting row it can move two squares forward if no pieces are blocking it
                if row == 1 and self.board[row + 2][col] == "--":
                    moves.append(Move((row, col), (row + 2, col), self.board))
            if col > 0 and self.board[row + 1][col - 1][0] == "w":  # there is a white piece to the left
                moves.append(Move((row, col), (row + 1, col - 1), self.board))
            if col < 7 and self.board[row + 1][col + 1][0] == "w":  # there is a white piece to the right
                moves.append(Move((row, col), (row + 1, col + 1), self.board))

    """
    Get all legal rook moves located at a specific row and column
    """
    def get_rook_moves(self, row, col, moves):
        forward_vertical_flag = True
        backward_vertical_flag = True
        right_horizontal_flag = True
        left_horizontal_flag = True
        # each for loop works the same way: pick a direction and keep going until you find a piece, adding valid moves
        if self.white_to_move:
            for i in range(1, 8):
                if row - i >= 0 and forward_vertical_flag:
                    if self.board[row - i][col] == "--":
                        moves.append(Move((row, col), (row - i, col), self.board))
                    elif self.board[row - i][col][0] == "b":
                        moves.append(Move((row, col), (row - i, col), self.board))
                        forward_vertical_flag = False
                    elif self.board[row - i][col][0] == "w":
                        forward_vertical_flag = False

            for i in range(1, 8):
                if row + i <= 7 and backward_vertical_flag:
                    if self.board[row + i][col] == "--":
                        moves.append(Move((row, col), (row + i, col), self.board))
                    elif self.board[row + i][col][0] == "b":
                        moves.append(Move((row, col), (row + i, col), self.board))
                        backward_vertical_flag = False
                    elif self.board[row + i][col][0] == "w":
                        backward_vertical_flag = False

            for i in range(1, 8):
                if col + i <= 7 and right_horizontal_flag:
                    if self.board[row][col + i] == "--":
                        moves.append(Move((row, col), (row, col + i), self.board))
                    elif self.board[row][col + i][0] == "b":
                        moves.append(Move((row, col), (row, col + i), self.board))
                        right_horizontal_flag = False
                    elif self.board[row][col + i][0] == "w":
                        right_horizontal_flag = False

            for i in range(1, 8):
                if col - i >= 0 and left_horizontal_flag:
                    if self.board[row][col - i] == "--":
                        moves.append(Move((row, col), (row, col - i), self.board))
                    elif self.board[row][col - i][0] == "b":
                        moves.append(Move((row, col), (row, col - i), self.board))
                        left_horizontal_flag = False
                    elif self.board[row][col - i][0] == "w":
                        left_horizontal_flag = False

        if not self.white_to_move:
            for i in range(1, 8):
                if row - i >= 0 and forward_vertical_flag:
                    if self.board[row - i][col] == "--":
                        moves.append(Move((row, col), (row - i, col), self.board))
                    elif self.board[row - i][col][0] == "w":
                        moves.append(Move((row, col), (row - i, col), self.board))
                        forward_vertical_flag = False
                    elif self.board[row - i][col][0] == "b":
                        forward_vertical_flag = False

            for i in range(1, 8):
                if row + i <= 7 and backward_vertical_flag:
                    if self.board[row + i][col] == "--":
                        moves.append(Move((row, col), (row + i, col), self.board))
                    elif self.board[row + i][col][0] == "w":
                        moves.append(Move((row, col), (row + i, col), self.board))
                        backward_vertical_flag = False
                    elif self.board[row + i][col][0] == "b":
                        backward_vertical_flag = False

            for i in range(1, 8):
                if col + i <= 7 and right_horizontal_flag:
                    if self.board[row][col + i] == "--":
                        moves.append(Move((row, col), (row, col + i), self.board))
                    elif self.board[row][col + i][0] == "w":
                        moves.append(Move((row, col), (row, col + i), self.board))
                        right_horizontal_flag = False
                    elif self.board[row][col + i][0] == "b":
                        right_horizontal_flag = False

            for i in range(1, 8):
                if col - i >= 0 and left_horizontal_flag:
                    if self.board[row][col - i] == "--":
                        moves.append(Move((row, col), (row, col - i), self.board))
                    elif self.board[row][col - i][0] == "w":
                        moves.append(Move((row, col), (row, col - i), self.board))
                        left_horizontal_flag = False
                    elif self.board[row][col - i][0] == "b":
                        left_horizontal_flag = False

    """
    Get all legal bishop moves located at a specific row and column
    """
    def get_bishop_moves(self, row, col, moves):
        #  same idea as rook moves: pick a direction and add moves until you hit a piece
        if self.white_to_move:
            plus_plus_flag = True
            plus_minus_flag = True
            minus_plus_flag = True
            minus_minus_flag = True
            for i in range(1, 8):
                if row + i <= 7 and col + i <= 7 and plus_plus_flag:
                    if self.board[row + i][col + i] == "--":
                        moves.append(Move((row, col), (row + i, col + i), self.board))
                    elif self.board[row + i][col + i][0] == "b":
                        moves.append(Move((row, col), (row + i, col + i), self.board))
                        plus_plus_flag = False
                    elif self.board[row + i][col + i][0] == "w":
                        plus_plus_flag = False

            for i in range(1, 8):
                if row + i <= 7 and col - i >= 0 and plus_minus_flag:
                    if self.board[row + i][col - i] == "--":
                        moves.append(Move((row, col), (row + i, col - i), self.board))
                    elif self.board[row + i][col - i][0] == "b":
                        moves.append(Move((row, col), (row + i, col - i), self.board))
                        plus_minus_flag = False
                    elif self.board[row + i][col - i][0] == "w":
                        plus_minus_flag = False

            for i in range(1, 8):
                if row - i >= 0 and col + i <= 7 and minus_plus_flag:
                    if self.board[row - i][col + i] == "--":
                        moves.append(Move((row, col), (row - i, col + i), self.board))
                    elif self.board[row - i][col + i][0] == "b":
                        moves.append(Move((row, col), (row - i, col + i), self.board))
                        minus_plus_flag = False
                    elif self.board[row - i][col + i][0] == "w":
                        minus_plus_flag = False

            for i in range(1, 8):
                if row - i >= 0 and col - i >= 0 and minus_minus_flag:
                    if self.board[row - i][col - i] == "--":
                        moves.append(Move((row, col), (row - i, col - i), self.board))
                    elif self.board[row - i][col - i][0] == "b":
                        moves.append(Move((row, col), (row - i, col - i), self.board))
                        minus_minus_flag = False
                    elif self.board[row - i][col - i][0] == "w":
                        minus_minus_flag = False

        elif not self.white_to_move:
            plus_plus_flag = True
            plus_minus_flag = True
            minus_plus_flag = True
            minus_minus_flag = True
            for i in range(1, 8):
                if row + i <= 7 and col + i <= 7 and plus_plus_flag:
                    if self.board[row + i][col + i] == "--":
                        moves.append(Move((row, col), (row + i, col + i), self.board))
                    elif self.board[row + i][col + i][0] == "w":
                        moves.append(Move((row, col), (row + i, col + i), self.board))
                        plus_plus_flag = False
                    elif self.board[row + i][col + i][0] == "b":
                        plus_plus_flag = False

            for i in range(1, 8):
                if row + i <= 7 and col - i >= 0 and plus_minus_flag:
                    if self.board[row + i][col - i] == "--":
                        moves.append(Move((row, col), (row + i, col - i), self.board))
                    elif self.board[row + i][col - i][0] == "w":
                        moves.append(Move((row, col), (row + i, col - i), self.board))
                        plus_minus_flag = False
                    elif self.board[row + i][col - i][0] == "b":
                        plus_minus_flag = False

            for i in range(1, 8):
                if row - i >= 0 and col + i <= 7 and minus_plus_flag:
                    if self.board[row - i][col + i] == "--":
                        moves.append(Move((row, col), (row - i, col + i), self.board))
                    elif self.board[row - i][col + i][0] == "w":
                        moves.append(Move((row, col), (row - i, col + i), self.board))
                        minus_plus_flag = False
                    elif self.board[row - i][col + i][0] == "b":
                        minus_plus_flag = False

            for i in range(1, 8):
                if row - i >= 0 and col - i >= 0 and minus_minus_flag:
                    if self.board[row - i][col - i] == "--":
                        moves.append(Move((row, col), (row - i, col - i), self.board))
                    elif self.board[row - i][col - i][0] == "w":
                        moves.append(Move((row, col), (row - i, col - i), self.board))
                        minus_minus_flag = False
                    elif self.board[row - i][col - i][0] == "b":
                        minus_minus_flag = False

    """
    Get all legal knight moves located at a specific row and column
    """
    def get_knight_moves(self, row, col, moves):

        def knight_moves_helper(self, row, col, moves, color):
            # tuples of (row, column) give every possible knight move from a current position
            knight_moves = [(1, 2), (-1, 2), (1, -2), (2, 1), (-2, 1), (2, -1), (-2, -1), (-1, -2)]
            for move in knight_moves:
                if 0 <= move[0] + row <= 7 and 0 <= move[1] + col <= 7:  # make sure the square is on the board
                    if self.board[move[0] + row][move[1] + col][0] != color:
                        moves.append(Move((row, col), (move[0] + row, move[1] + col), self.board))

        if self.white_to_move:
            knight_moves_helper(self, row, col, moves, "w")

        if not self.white_to_move:
            knight_moves_helper(self, row, col, moves, "b")

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
        # TODO disallow moves that put the king in check
        def king_moves_helper(self, row, col, moves, color):
            king_moves = [(0, 1), (0, -1), (1, -1), (1, 0), (1, 1), (-1, -1), (-1, 0), (-1, 1)]
            for move in king_moves:
                if 0 <= move[0] + row <= 7 and 0 <= move[1] + col <= 7:  # make sure the square is on the board
                    if self.board[move[0] + row][move[1] + col][0] != color:
                        moves.append(Move((row, col), (move[0] + row, move[1] + col), self.board))

        if self.white_to_move:
            king_moves_helper(self, row, col, moves, "w")

        if not self.white_to_move:
            king_moves_helper(self, row, col, moves, "b")


class Move:
    # maps keys to values
    # key : value
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                     "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3,
                     "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_square, end_square, board):
        self.start_row = start_square[0]
        self.start_col = start_square[1]
        self.end_row = end_square[0]
        self.end_col = end_square[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.move_ID = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col

    """
    Overriding the equals method
    """
    def __eq__(self, other):
        if isinstance(other, Move):
            return other.move_ID == self.move_ID
        return False

    def get_chess_notation(self):
        # TODO make this real Chess notation - add logic for check/checkmate
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



