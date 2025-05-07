import pygame
import os
from chess import Board, Move
import socket

HOST = '127.0.0.1'
PORT = 65432

def data_to_arr(data):
    message = data.decode('utf-8')
    message = message.split(' ')
    message = [eval(num) for num in message]
    return message

def move_to_data(move):
    message = "1 " + str(move.fromx) + " " + str(move.fromy) + " " + str(move.tox) + " " + str(move.toy)
    data = message.encode('utf-8')
    return data

def setup_socket():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    data = s.recv(4)
    col = eval(data.decode('utf-8'))
    print("color white") if col == 1 else print("color black")
    s.send(int(1).to_bytes())
    s.settimeout(0.0)
    return s, col

def try_to_receive_data(s):
    move = None
    try:
        data = s.recv(10)
        print(data)
        if data:
            message = data_to_arr(data)
            move = Move(message[1], message[2], message[3], message[4])
            board.move_piece(move)
    except:
        pass
    return move


pygame.init()

WIDTH, HEIGHT = 640, 640
ROWS, COLS = 8, 8
SQ_SIZE = WIDTH // COLS

WHITE = (240, 217, 181)
BLACK = (181, 136, 99)

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
            piece = None
            if p_color == 1:
                piece = board_obj.board[row][col]
            else:
                piece = board_obj.board[7-row][7-col]
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
    if p_color != 1:
        x, y = WIDTH - x, HEIGHT - y
    return x // SQ_SIZE, y // SQ_SIZE

board = Board()
dragging = False
drag_piece = None
start_coords = None

running = True

s, p_color = setup_socket()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("White Chess") if p_color == 1 else pygame.display.set_caption("Black Chess")
clock = pygame.time.Clock()

while running:
    clock.tick(60)
    mouse_pos = pygame.mouse.get_pos()

    move = try_to_receive_data(s)
    if move is not None:
        board.move_piece(move)
    

    winner = board.checkWin()
    if winner != 0:
        if winner == 1:
            win_text = "White wins!"
        else:
            win_text = "Black wins!"
        font = pygame.font.SysFont(None, 64)
        text_surface = font.render(win_text, True, (0, 255, 0))
        text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(text_surface, text_rect)
        pygame.display.flip()
        
        pygame.time.delay(3000)
        running = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = get_board_coords(mouse_pos)
            if board.isOccupied(x, y) == p_color:
                drag_piece = board.board[y][x]
                start_coords = (x, y)
                dragging = True

        elif event.type == pygame.MOUSEBUTTONUP and dragging:
            end_x, end_y = get_board_coords(mouse_pos)
            move = Move(start_coords[0], start_coords[1], end_x, end_y)
            if board.is_valid(move) and board.isOccupied(move.fromx, move.fromy) == p_color:
                data = move_to_data(move)
                s.send(data)
            dragging = False
            drag_piece = None
            start_coords = None

    draw_board()
    draw_pieces(board, drag_piece if dragging else None, mouse_pos if dragging else None)
    pygame.display.flip()

pygame.quit()
