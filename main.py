"""
Responsible for handling user input and current game state object
"""

import pygame as p
import engine
import smart_move_finder

p.init()
BOARD_WIDTH = BOARD_HEIGHT = 512
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8
SQ_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

# TODO pre-moves, player select/config, material count, opening book,
#  square labels, draw rules, time control, drag and drop

"""
Initialize a global dictionary of images. This will only be called once in the main function
"""


def load_images():
    # TODO implement alternate piece image options
    pieces = ['wP', 'wN', 'wB', 'wR', 'wQ', 'wK', 'bP', 'bN', 'bB', 'bR', 'bQ', 'bK']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
    # Note: we can access an image by saying 'IMAGES['wP']'


"""
The main driver for the game. This will handle user input and updating the graphics
"""


def main():
    p.init()
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    move_log_font = p.font.SysFont("Arial", 12, False, False)
    gs = engine.GameState()
    valid_moves = gs.get_valid_moves()
    move_made = False  # flag variable for when a move is made
    animate = False  # flag variable for turning off animation
    load_images()
    square_selected = ()  # Tuple that keeps track of the last row/column the player selected (tuple: (row, col))
    player_clicks = []  # list that keeps track of two consecutive player clicks (two tuples: [(5, 4), (6, 8)])
    game_over = False
    player_one = True  # if a human is playing white, this will be true
    player_two = False  # same as above but for black
    running = True
    while running:
        human_turn = (gs.white_to_move and player_one) or (not gs.white_to_move and player_two)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over and human_turn:
                    location = p.mouse.get_pos()  # (x, y) of mouse click position
                    col = location[0] // SQ_SIZE  # get column number from location
                    row = location[1] // SQ_SIZE  # get row number from location
                    if square_selected == (row, col) or col >= 8:  # if the player selects the same square twice or clicked the move log
                        square_selected = ()  # deselect
                        player_clicks = []  # clear player_clicks
                    else:  # if the player clicks on a piece or empty square
                        square_selected = (row, col)
                        player_clicks.append(square_selected)  # appends for both 1st or 2nd click
                    if len(player_clicks) == 2:  # after second click
                        move = engine.Move(player_clicks[0], player_clicks[1], gs.board)
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:  # execute the move only if it is valid
                                gs.make_move(valid_moves[i])
                                move_made = True
                                animate = True
                                square_selected = ()  # reset square_selected
                                player_clicks = []  # reset player_clicks
                        if not move_made:  # if the player did not make a valid move (e.g. clicked on another ally piece)
                            player_clicks = [square_selected]  # avoid bug where you double click to select new piece
            # key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # undo move when 'z' is pressed
                    gs.undo_move()
                    move_made = True
                    animate = False
                    game_over = False
                if e.key == p.K_r:  # restart the game when you press "r"
                    # TODO add dialog box to confirm player wants to restart the game
                    gs = engine.GameState()
                    valid_moves = gs.get_valid_moves()
                    square_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    game_over = False

        # AI move finder logic
        if not game_over and not human_turn:
            AI_move = smart_move_finder.find_best_move(gs, valid_moves)
            if AI_move is None:
                AI_move = smart_move_finder.find_random_move(valid_moves)
            gs.make_move(AI_move)
            move_made = True
            animate = True

        if move_made:
            if animate:
                animate_move(gs.move_log[-1], screen, gs.board, clock)
            valid_moves = gs.get_valid_moves()
            move_made = False
            animate = False

        draw_game_state(screen, gs, valid_moves, square_selected, move_log_font)

        if gs.checkmate or gs.stalemate:
            game_over = True
            text = "Stalemate" if gs.stalemate else "Black wins by checkmate" if gs.white_to_move else "White wins by checkmate"
            draw_end_game_text(screen, text)

        clock.tick(MAX_FPS)
        p.display.flip()


"""
Responsible for all graphics in the current game state
"""


def draw_game_state(screen, gs, valid_moves, square_selected, move_log_font):
    draw_board(screen)  # draw squares on the board
    highlight_squares(screen, gs, valid_moves, square_selected)  # highlight squares
    draw_pieces(screen, gs.board)  # draw pieces on squares
    draw_move_log(screen, gs, move_log_font)


"""
Draw the squares on the board
"""


def draw_board(screen):
    global colors
    # TODO implement alternate color choices
    colors = [p.Color("white"), p.Color("gray")]
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[((row + col) % 2)]
            p.draw.rect(screen, color, p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))


"""
Highlight the square selected and possible moves for the piece selected
"""


def highlight_squares(screen, gs, valid_moves, square_selected):
    # TODO change highlighting last piece moved
    if square_selected != ():  # check that the square has a piece
        row, col = square_selected
        if gs.board[row][col][0] == ("w" if gs.white_to_move else "b"):  # check that the piece selected is not an enemy piece
            # highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)  # set the transparency: 0 = transparent, 255 = opaque
            s.fill(p.Color('blue'))
            screen.blit(s, (col * SQ_SIZE, row * SQ_SIZE))
            # highlight moves from that square
            s.fill(p.Color('yellow'))
            for move in valid_moves:
                if move.start_row == row and move.start_col == col:
                    screen.blit(s, (SQ_SIZE * move.end_col, SQ_SIZE * move.end_row))

    # highlight the square of the piece that last moved
    if gs.move_log:  # make sure the move log is not empty
        last_move = gs.move_log[-1]  # get the last move
        s = p.Surface((SQ_SIZE, SQ_SIZE))
        s.fill(p.Color('yellow'))
        s.set_alpha(100)
        screen.blit(s, (SQ_SIZE * last_move.end_col, SQ_SIZE * last_move.end_row))


"""
Draw the pieces on the board
"""


def draw_pieces(screen, board):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != "--":  # not an empty square
                screen.blit(IMAGES[piece], p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))


"""
draws the move log on the side of the board
"""


def draw_move_log(screen, gs, move_log_font):
    move_log_rect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("black"), move_log_rect)
    move_log = gs.move_log
    move_texts = []
    for i in range(0, len(move_log), 2):
        move_string = str(i//2 + 1) + ". " + str(move_log[i]) + " "
        if i + 1 < len(move_log):
            move_string += str(move_log[i + 1]) + "   "
        move_texts.append(move_string)

    moves_per_row = 3
    padding = 5
    line_spacing = 2
    textY = padding
    for i in range(0, len(move_texts), moves_per_row):
        text = ""
        for j in range(moves_per_row):
            if i + j < len(move_texts):
                text += move_texts[i + j]
        text_object = move_log_font.render(text, True, p.Color("white"))
        text_location = move_log_rect.move(padding, textY)
        screen.blit(text_object, text_location)
        textY += text_object.get_height() + line_spacing


"""
animating a move
"""


def animate_move(move, screen, board, clock):
    global colors
    dr = move.end_row - move.start_row
    dc = move.end_col - move.start_col
    frames_per_square = 2  # frames to move one square
    frame_count = (abs(dr) + abs(dc)) * frames_per_square
    for frame in range(frame_count + 1):
        row, col = (move.start_row + dr * frame / frame_count, move.start_col + dc * frame / frame_count)
        draw_board(screen)
        draw_pieces(screen, board)
        # erase the piece from its end square
        color = colors[(move.end_row + move.end_col) % 2]
        end_square = p.Rect(move.end_col * SQ_SIZE, move.end_row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, end_square)
        # draw captured piece onto rectangle
        if move.piece_captured != "--":
            if move.en_passant_move:
                en_passant_row = move.end_row + 1 if move.piece_captured[0] == "b" else move.end_row - 1
                end_square = p.Rect(move.end_col * SQ_SIZE, en_passant_row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.piece_captured], end_square)
        # draw moving piece
        screen.blit(IMAGES[move.piece_moved], p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)


"""
draws the text on the screen after the game is over
"""


def draw_end_game_text(screen, text):
    font = p.font.SysFont("Helvetica", 32, True, False)
    text_object = font.render(text, 0, p.Color("Black"))
    text_location = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - text_object.get_width() / 2, BOARD_HEIGHT / 2 - text_object.get_height() / 2)
    screen.blit(text_object, text_location.move(2, 2))


if __name__ == "__main__":
    main()
