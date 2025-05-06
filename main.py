import pygame
import os
from chess import Board, Move

pygame.init()

WIDTH, HEIGHT = 640, 640
ROWS, COLS = 8, 8
SQ_SIZE = WIDTH // COLS

WHITE = (240, 217, 181)
BLACK = (181, 136, 99)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess")
clock = pygame.time.Clock()

PIECES = {}
for color in ['w', 'b']:
    for piece in ['K', 'Q', 'R', 'B', 'N', 'P']:
        name = color + piece
        script_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(script_dir, "assets", name + ".png")
        image = pygame.image.load(path)
        image = pygame.transform.scale(image, (SQ_SIZE, SQ_SIZE))
        PIECES[name] = image

def draw_board():
    for row in range(ROWS):
        for col in range(COLS):
            color = WHITE if (row + col) % 2 == 0 else BLACK
            pygame.draw.rect(screen, color, (col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def draw_pieces(board_obj, dragging_piece=None, dragging_pos=None):
    for row in range(ROWS):
        for col in range(COLS):
            piece = board_obj.board[row][col]
            key = str(piece).strip()
            if key and (piece != dragging_piece):
                img = PIECES.get(key)
                if img:
                    screen.blit(img, (col * SQ_SIZE, row * SQ_SIZE))

    if dragging_piece and dragging_pos:
        key = str(dragging_piece).strip()
        img = PIECES.get(key)
        if img:
            screen.blit(img, (dragging_pos[0] - SQ_SIZE // 2, dragging_pos[1] - SQ_SIZE // 2))

def get_board_coords(mouse_pos):
    x, y = mouse_pos
    return x // SQ_SIZE, y // SQ_SIZE

board = Board()
dragging = False
drag_piece = None
start_coords = None

running = True
while running:
    clock.tick(60)
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = get_board_coords(mouse_pos)
            if board.isOccupied(x, y):
                drag_piece = board.board[y][x]
                start_coords = (x, y)
                dragging = True

        elif event.type == pygame.MOUSEBUTTONUP and dragging:
            end_x, end_y = get_board_coords(mouse_pos)
            move = Move(start_coords[0], start_coords[1], end_x, end_y)
            if board.is_valid(move):
                board.move_piece(move)
            dragging = False
            drag_piece = None
            start_coords = None

    draw_board()
    draw_pieces(board, drag_piece if dragging else None, mouse_pos if dragging else None)
    pygame.display.flip()

pygame.quit()
