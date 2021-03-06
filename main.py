"""
Responsible for handling user input and current game state object
"""

import pygame as p
import engine
import smart_move_finder
from multiprocessing import Process, Queue
import sys

p.init()
BOARD_WIDTH = BOARD_HEIGHT = 512
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8
SQ_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}


# TODO pre-moves, opening book,
#  square labels, draw rules, variants: 960, chess squared, three check, King of the Hill,
#  keep score, option to resign or draw

"""
Configure the game
"""


class Button:
    def __init__(self, button_text, button_location, button_width):
        self.button_text = button_text
        self.button_location = button_location
        self.button_width = button_width
        self.button_height = 35
        self.button_rect = p.Rect(self.button_location[0], self.button_location[1], self.button_width, self.button_height)
        self.selected = False
        self.selected_color = p.Color("cyan")

    def draw_button(self, screen):
        # draw the rectangle
        color = self.selected_color if self.selected else p.Color("white")
        p.draw.rect(screen, color, self.button_rect)

        # draw the text
        font = p.font.SysFont("Helvetica", 20, False, False)
        text_object = font.render(self.button_text, 1, p.Color("Black"))
        text_location = (self.button_location[0] + self.button_width//6, self.button_location[1] + self.button_height//6)
        screen.blit(text_object, text_location)


start_button = Button("Start Game", (BOARD_WIDTH - 50, BOARD_HEIGHT - 50), 150)
white_select_button = Button("White", (25, 25), 75)
black_select_button = Button("Black", (25, 75), 75)
time_3_0_button = Button("3+0", (200, 25), 60)
time_3_2_button = Button("3+2", (200, 75), 60)
time_5_0_button = Button("5+0", (200, 125), 60)
white_button = Button("White", (375, 25), 85)
beige_button = Button("Beige", (375, 75), 85)
ivory_button = Button("Ivory", (375, 125), 85)
gray_button = Button("Gray", (525, 25), 85)
dark_gray_button = Button("Dark Gray", (525, 75), 85)
green_button = Button("Dark Green", (525, 125), 150)

buttons = [start_button, white_select_button, black_select_button, time_3_0_button, time_3_2_button, time_5_0_button, white_button, beige_button, ivory_button, gray_button, dark_gray_button, green_button]
time_buttons = [time_3_0_button, time_3_2_button, time_5_0_button]
piece_color_buttons = [white_select_button, black_select_button]
light_color_buttons = [white_button, beige_button, ivory_button]
dark_color_buttons = [gray_button, dark_gray_button, green_button]

def config():
    p.init()
    p.display.set_caption('Pygame Chess')
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    start_button_enable = False
    running = True
    while running:
        screen.fill(p.Color("black"))
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()  # (x, y) of mouse click position
                for button in buttons:
                    if button.button_rect.collidepoint(location):  # press the button
                        button.selected = not button.selected
                        for time_button in time_buttons:  # deselect other time control buttons
                            if button in time_buttons and button != time_button:
                                time_button.selected = False
                        for color_button in piece_color_buttons:  # deselect other color button
                            if button in piece_color_buttons and button != color_button:
                                color_button.selected = False
                        for light_color_button in light_color_buttons:  # deselect other color button
                            if button in light_color_buttons and button != light_color_button:
                                light_color_button.selected = False
                        for dark_color_button in dark_color_buttons:  # deselect other color button
                            if button in dark_color_buttons and button != dark_color_button:
                                dark_color_button.selected = False
                        if not start_button_enable:  # don't allow game to start until valid choices are made
                            start_button.selected = False

        for button in buttons:  # draw buttons
            button.draw_button(screen)

        if (white_select_button.selected or black_select_button.selected) and (time_3_0_button.selected or time_3_2_button.selected or time_5_0_button.selected):  # don't let user start game without setting up
            start_button_enable = True

        player_one = True if white_select_button.selected else False
        time_control = 300 if time_5_0_button.selected else 180
        increment = 2 if time_3_2_button.selected else 0
        for button in light_color_buttons:
            if button.selected:
                light_square_color = p.Color(button.button_text)
        for button in dark_color_buttons:
            if button.selected:
                dark_square_color = p.Color(button.button_text)

        if start_button.selected:
            main(player_one, time_control, increment, light_square_color, dark_square_color)  # call the main game loop

        clock.tick(MAX_FPS)
        p.display.flip()

    p.quit()  # quits pygame
    sys.exit()


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


def main(player_one, time_control, increment, light_square_color, dark_square_color):
    p.init()
    p.display.set_caption('Pygame Chess')
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    move_log_font = p.font.SysFont("Arial", 12, False, False)
    gs = engine.GameState()
    valid_moves = gs.get_valid_moves()
    r = Restart()
    move_made = False  # flag variable for when a move is made
    animate = False  # flag variable for turning off animation
    load_images()
    square_selected = ()  # Tuple that keeps track of the last row/column the player selected (tuple: (row, col))
    player_clicks = []  # list that keeps track of two consecutive player clicks (two tuples: [(5, 4), (6, 8)])
    game_over = False
    premove = None
    player_two = not player_one  # True means human player
    AI_thinking = False
    move_finder_process = None
    move_undone = False
    time_since_last_tick = 0
    time_remaining = time_control
    light_square_color = light_square_color
    dark_square_color = dark_square_color
    lost_on_time = False
    running = True
    while running:
        if time_remaining <= 0.0:
            time_remaining = 0
            game_over = True
            lost_on_time = True

        human_turn = (gs.white_to_move and player_one) or (not gs.white_to_move and player_two)
        if human_turn and not game_over:
            time_remaining -= time_since_last_tick / 1000
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # mouse handler
            elif e.type == p.MOUSEBUTTONUP:
                if len(player_clicks) == 1:  # if the player clicked and grabbed a piece
                    location = p.mouse.get_pos()  # (x, y) of mouse click position
                    col = location[0] // SQ_SIZE  # get column number from location
                    row = location[1] // SQ_SIZE  # get row number from location
                    if square_selected != (row, col):  # if the player drags the mouse
                        square_selected = (row, col)
                        player_clicks.append(square_selected)
                        if human_turn:  # if it's a human turn, play the move
                            move = engine.Move(player_clicks[0], player_clicks[1], gs.board)
                            for i in range(len(valid_moves)):
                                if move == valid_moves[i]:  # execute the move only if it is valid
                                    gs.make_move(valid_moves[i])
                                    move_made = True
                                    animate = True
                                    time_remaining += increment
                                    square_selected = ()  # reset square_selected
                                    player_clicks = []  # reset player_clicks
                            if not move_made:  # if the player did not make a valid move (e.g. clicked on another ally piece)
                                player_clicks = [square_selected]  # avoid bug where you double click to select new piece
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over and not r.restart_requested:
                    location = p.mouse.get_pos()  # (x, y) of mouse click position
                    col = location[0] // SQ_SIZE  # get column number from location
                    row = location[1] // SQ_SIZE  # get row number from location
                    if square_selected == (row, col) or col >= 8:  # if the player selects the same square twice or clicked the move log
                        square_selected = ()  # deselect
                        player_clicks = []  # clear player_clicks
                    else:  # if the player clicks on a piece or empty square
                        square_selected = (row, col)
                        player_clicks.append(square_selected)  # appends for both 1st or 2nd click
                    if len(player_clicks) == 2 or premove:  # after second click
                        if human_turn:  # if it's a human turn, play the move
                            move = engine.Move(player_clicks[0], player_clicks[1], gs.board)
                            for i in range(len(valid_moves)):
                                if move == valid_moves[i]:  # execute the move only if it is valid
                                    gs.make_move(valid_moves[i])
                                    # premove = None
                                    move_made = True
                                    animate = True
                                    time_remaining += increment
                                    square_selected = ()  # reset square_selected
                                    player_clicks = []  # reset player_clicks
                            if not move_made:  # if the player did not make a valid move (e.g. clicked on another ally piece)
                                player_clicks = [square_selected]  # avoid bug where you double click to select new piece
                        # else:  # if it's not a human turn, save the move as a premove
                        #    premove = engine.Move(player_clicks[0], player_clicks[1], gs.board)
                elif r.restart_requested:
                    location = p.mouse.get_pos()  # (x, y) of mouse click position
                    r.capture_response(location)
            # key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # undo move when 'z' is pressed
                    gs.undo_move()
                    move_made = True
                    animate = False
                    game_over = False
                    if AI_thinking:
                        move_finder_process.terminate()
                        AI_thinking = False
                    move_undone = True
                if e.key == p.K_r:  # restart the game when you press "r"
                    r.restart_requested = True

        # AI move finder logic
        if not game_over and not human_turn and not move_undone and not r.restart_requested:
            if not AI_thinking:
                AI_thinking = True
                print("Thinking...")
                return_queue = Queue()  # used to pass data between threads
                move_finder_process = Process(target=smart_move_finder.find_best_move, args=(gs, valid_moves, return_queue))
                move_finder_process.start()  # calls find_best_move in its own thread

            if not move_finder_process.is_alive():
                print("Done thinking")
                AI_move = return_queue.get()
                if AI_move is None:
                    AI_move = smart_move_finder.find_random_move(valid_moves)
                gs.make_move(AI_move)
                move_made = True
                animate = True
                AI_thinking = False

        if move_made:
            if animate:
                animate_move(gs.move_log[-1], screen, gs.board, clock, light_square_color, dark_square_color)
            valid_moves = gs.get_valid_moves()
            move_made = False
            animate = False
            move_undone = False

        draw_game_state(screen, gs, valid_moves, square_selected, move_log_font, time_remaining, light_square_color, dark_square_color)

        if lost_on_time:
            text = "White wins on time" if not gs.white_to_move else "Black wins on time"
            draw_end_game_text(screen, text)

        if gs.checkmate or gs.stalemate:
            game_over = True
            text = "Stalemate" if gs.stalemate else "Black wins by checkmate" if gs.white_to_move else "White wins by checkmate"
            draw_end_game_text(screen, text)

        if r.restart_requested:
            r.draw_game_restart_confirmation(screen)

        if r.restart_confirmed:
            gs = engine.GameState()
            valid_moves = gs.get_valid_moves()
            square_selected = ()
            player_clicks = []
            move_made = False
            animate = False
            game_over = False
            if AI_thinking:
                move_finder_process.terminate()
                AI_thinking = False
            move_undone = True
            lost_on_time = False
            r.restart_confirmed = False
            time_remaining = time_control

        time_since_last_tick = clock.tick(MAX_FPS)
        p.display.flip()

    p.quit()  # quits pygame
    sys.exit()


"""
Responsible for all graphics in the current game state
"""


def draw_game_state(screen, gs, valid_moves, square_selected, move_log_font, time_remaining, light_square_color, dark_square_color):
    draw_board(screen, light_square_color, dark_square_color)  # draw squares on the board
    highlight_squares(screen, gs, valid_moves, square_selected)  # highlight squares
    draw_pieces(screen, gs.board)  # draw pieces on squares
    draw_move_log(screen, gs, move_log_font)
    draw_material_count(screen, smart_move_finder, gs)
    draw_clock(screen, time_remaining)


"""
Draw the squares on the board
"""


def draw_board(screen, light_square_color, dark_square_color):
    global colors
    # TODO implement alternate color choices
    colors = [light_square_color, dark_square_color]
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


def draw_material_count(screen, smart_move_finder, gs):
    material_count = str(smart_move_finder.score_board(gs))
    font = p.font.SysFont("Helvetica", 14, True, False)
    text_object = font.render("Material Count: " + material_count, 1, p.Color("White"))
    text_location = p.Rect(BOARD_WIDTH + 15, BOARD_HEIGHT - 25, 50, 50)
    screen.blit(text_object, text_location)


"""
animating a move
"""


def animate_move(move, screen, board, clock, light_square_color, dark_square_color):
    global colors
    dr = move.end_row - move.start_row
    dc = move.end_col - move.start_col
    frames_per_square = 2  # frames to move one square
    frame_count = (abs(dr) + abs(dc)) * frames_per_square
    for frame in range(frame_count + 1):
        row, col = (move.start_row + dr * frame / frame_count, move.start_col + dc * frame / frame_count)
        draw_board(screen, light_square_color, dark_square_color)
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
prompt user to confirm that they want to restart the game
"""


class Restart:
    def __init__(self):
        self.restart_requested = False
        self.restart_confirmed = False
        self.yes_button = p.Rect(0, 0, 0, 0)
        self.no_button = p.Rect(0, 0, 0, 0)

    def draw_game_restart_confirmation(self, screen):
        # main message box
        box_color = "black"
        box_width = BOARD_WIDTH//2
        box_height = BOARD_HEIGHT//4
        box_x = BOARD_WIDTH//2 - box_width//2
        box_y = BOARD_HEIGHT//2 - box_height//2
        box_rect = p.Rect(box_x, box_y, box_width, box_height)

        # yes button
        yes_color = "white"
        yes_x = box_x + box_x//4
        yes_y = box_y + box_y//3
        yes_width = box_width//4
        yes_height = box_height//4
        self.yes_button = p.Rect(yes_x, yes_y, yes_width, yes_height)

        # no button
        no_color = "white"
        no_x = box_x*2 + box_x//4
        no_y = box_y + box_y//3
        no_width = box_width//4
        no_height = box_height//4
        self.no_button = p.Rect(no_x, no_y, no_width, no_height)

        # draw box and buttons
        p.draw.rect(screen, box_color, box_rect)
        p.draw.rect(screen, yes_color, self.yes_button)
        p.draw.rect(screen, no_color, self.no_button)

        # confirmation text
        font = p.font.SysFont("Helvetica", 14, True, False)
        text_object = font.render("Are you sure you want to restart?", 1, p.Color("White"))
        text_location = (box_x + 12, box_y + box_y//8)
        screen.blit(text_object, text_location)

        # yes text
        font = p.font.SysFont("Helvetica", 14, True, False)
        text_object = font.render("Yes", 1, p.Color("Black"))
        text_location = (yes_x + yes_width//4, yes_y + yes_height//4)
        screen.blit(text_object, text_location)

        # no text
        text_object = font.render("No", 1, p.Color("Black"))
        text_location = (no_x + no_width//3, no_y + no_height // 4)
        screen.blit(text_object, text_location)

    def capture_response(self, location):
        if self.yes_button.collidepoint(location):
            self.restart_requested = False
            self.restart_confirmed = True
        elif self.no_button.collidepoint(location):
            self.restart_requested = False


"""
draw the time clock
"""


def draw_clock(screen, time_remaining):
    if time_remaining <= 0.0:
        time_remaining = 0
    m, s = divmod(time_remaining, 60)
    m, s = int(m//1), round(s, 1)
    time_remaining_str = str(m) + ":" + str(s)
    font = p.font.SysFont("Helvetica", 14, True, False)
    text_object = font.render(time_remaining_str, 1, p.Color("White"))
    text_location = (BOARD_WIDTH + 15, BOARD_HEIGHT-50)
    screen.blit(text_object, text_location)


"""
draws the text on the screen after the game is over
"""


def draw_end_game_text(screen, text):
    font = p.font.SysFont("Helvetica", 32, True, False)
    text_object = font.render(text, 0, p.Color("Black"))
    text_location = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - text_object.get_width() / 2, BOARD_HEIGHT / 2 - text_object.get_height() / 2)
    screen.blit(text_object, text_location.move(2, 2))


if __name__ == "__main__":
    config()