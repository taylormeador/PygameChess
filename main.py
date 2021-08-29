"""
Responsible for handling user input and current game state object
"""

import pygame as p
from Chess import engine

p.init()
WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

"""
Initialize a global dictionary of images. This will only be called once in the main function
"""


def load_images():
    # TODO implement alternate piece options
    pieces = ['wP', 'wN', 'wB', 'wR', 'wQ', 'wK', 'bP', 'bN', 'bB', 'bR', 'bQ', 'bK']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("Chess/images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
    # Note: we can access an image by saying 'IMAGES['wP']'


"""
The main driver for the game. This will handle user input and updating the graphics
"""


def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = engine.GameState()
    valid_moves = gs.get_valid_moves()
    move_made = False  # flag variable for when a move is made
    load_images()
    square_selected = ()  # Tuple that keeps track of the last row/column the player selected (tuple: (row, col))
    player_clicks = []  # list that keeps track of two consecutive player clicks (two tuples: [(5, 4), (6, 8)])
    running = True
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # mouse handlers
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()  # (x, y) of mouse click position
                col = location[0] // SQ_SIZE  # get column number from location
                row = location[1] // SQ_SIZE  # get row number from location
                if square_selected == (row, col):  # if the player selects the same square twice
                    square_selected = ()  # deselect
                    player_clicks = []  # clear player_clicks
                else:  # if the player clicks on a piece or empty square
                    square_selected = (row, col)
                    player_clicks.append(square_selected)  # appends for both 1st or 2nd click
                if len(player_clicks) == 2:  # after second click
                    move = engine.Move(player_clicks[0], player_clicks[1], gs.board)
                    if move in valid_moves:  # execute the move only if it is valid
                        gs.make_move(move)
                        move_made = True
                        print(move.get_chess_notation())
                        square_selected = ()  # reset square_selected
                        player_clicks = []  # reset player_clicks
                    else:  # if the player did not make a valid move (e.g. clicked on another ally piece)
                        player_clicks = [square_selected]  # avoid bug where you double click to select new piece
            # key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # undo move when 'z' is pressed
                    gs.undo_move()
                    move_made = True

        if move_made:
            valid_moves = gs.get_valid_moves()
            move_made = False

        draw_game_state(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()


"""
Responsible for all graphics in the current game state
"""


def draw_game_state(screen, gs):
    draw_board(screen)  # draw squares on the board
    draw_pieces(screen, gs.board)  # draw pieces on squares


"""
Draw the squares on the board
"""


def draw_board(screen):
    # TODO implement alternate color choices
    colors = [p.Color("white"), p.Color("gray")]
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[((row + col) % 2)]
            p.draw.rect(screen, color, p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))


"""
Draw the pieces on the board
"""


def draw_pieces(screen, board):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != "--":  # not an empty square
                screen.blit(IMAGES[piece], p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))


if __name__ == "__main__":
    main()
