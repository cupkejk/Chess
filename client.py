import pygame
import os
from chess import Board, Move
import socket
from time import sleep
import sys

if len(sys.argv) > 1:
    ip = sys.argv[1]
else:
    ip = "localhost"

HOST = ip
PORT = 65432

STAMINA_BAR_WIDTH = 30
STAMINA_BAR_PADDING = 10
STAMINA_BAR_BG_COLOR = (50, 50, 50)
STAMINA_BAR_FG_COLOR_RED = (200, 0, 0)
STAMINA_BAR_FG_COLOR_GREEN = (0, 200, 0)

def data_to_arr(data):
    message = data.decode('utf-8')
    message = message.split(' ')
    message = [eval(num) for num in message]
    return message

def move_to_data(move):
    message = "1 " + str(move.fromx) + " " + str(move.fromy) + " " + str(move.tox) + " " + str(move.toy)
    data = message.encode('utf-8')
    return data

def arr_to_move(arr):
    if(arr[0] != 1): return None
    
    move = Move(arr[1], arr[2], arr[3], arr[4])
    return move, arr[5]

def setup_socket():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    data = s.recv(4)
    col = eval(data.decode('utf-8'))
    s.send(int(1).to_bytes())
    s.settimeout(0.0)
    return s, col

def try_to_receive_data(s):
    move = None
    stamina = None
    try:
        data = s.recv(100)
        printLog(data)
        if data:
            arr = data_to_arr(data)
            move, stamina = arr_to_move(arr)
    except:
        pass
    return move, stamina

def printLog(log):
    print("DEBUG INFO:", log)



pygame.init()


BOARD_WIDTH, BOARD_HEIGHT = 640, 640
WIDTH, HEIGHT = 640 + STAMINA_BAR_WIDTH + STAMINA_BAR_PADDING*2, 640
ROWS, COLS = 8, 8
SQ_SIZE = BOARD_WIDTH // COLS

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
    global dragging
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
        if p_color == 1:
            if key[0] == 'b':
                dragging = False
                return
        else:
            if key[0] == 'w':
                dragging = False
                return
        img = PIECES.get(key)
        if img:
            screen.blit(img, (dragging_pos[0] - SQ_SIZE // 2, dragging_pos[1] - SQ_SIZE // 2))

def draw_stamina_bar(surface, current_stamina_val, max_stamina_val):
    bar_outer_x = BOARD_WIDTH + STAMINA_BAR_PADDING
    bar_outer_y = STAMINA_BAR_PADDING
    bar_actual_width = STAMINA_BAR_WIDTH
    bar_actual_height = BOARD_HEIGHT - (2 * STAMINA_BAR_PADDING)

    pygame.draw.rect(surface, STAMINA_BAR_BG_COLOR, (BOARD_WIDTH, 0, STAMINA_BAR_PADDING*2+STAMINA_BAR_WIDTH, STAMINA_BAR_PADDING+HEIGHT))

    fill_ratio = 0
    if max_stamina_val > 0:
        fill_ratio = current_stamina_val / max_stamina_val
    fill_ratio = max(0.0, min(1.0, fill_ratio))

    fill_height = int(fill_ratio * bar_actual_height)

    if board.deltaLastMove(p_color) < 1: col = STAMINA_BAR_FG_COLOR_RED
    else: col = STAMINA_BAR_FG_COLOR_GREEN
    pygame.draw.rect(surface, col,
                     (bar_outer_x, bar_outer_y + (bar_actual_height - fill_height),
                      bar_actual_width, fill_height))
    
    pygame.draw.rect(surface, (200,200,200), (bar_outer_x, bar_outer_y, bar_actual_width, bar_actual_height), 1)

    #paski
    for i in range(1, board.MAX_STAMINA):
        x = bar_outer_x
        y = STAMINA_BAR_PADDING + bar_actual_height*i/board.MAX_STAMINA
        pygame.draw.rect(surface, (255, 255, 255), (x, y, STAMINA_BAR_WIDTH, 1))

def get_board_coords(mouse_pos):
    x, y = mouse_pos
    if p_color != 1:
        x, y = BOARD_WIDTH - x, BOARD_HEIGHT - y
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
    dt = clock.tick(60) / 1000.0

    board.updateStamina()

    mouse_pos = pygame.mouse.get_pos()
    move, stamina = try_to_receive_data(s)
    if move is not None:
        board.move_piece(move)
        board.setStamina(p_color, stamina)
    

    winner = board.checkWin()
    if winner != 0:
        if winner == 1:
            win_text = "White wins!"
        else:
            win_text = "Black wins!"
        font = pygame.font.SysFont(None, 64)
        text_surface = font.render(win_text, True, (0, 255, 0))
        text_rect = text_surface.get_rect(center=(BOARD_WIDTH // 2, BOARD_HEIGHT // 2))
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
    draw_stamina_bar(screen, board.getStamina(p_color), board.MAX_STAMINA)
    draw_pieces(board, board.board[y][x] if dragging else None, mouse_pos if dragging else None)
    
    pygame.display.flip()

pygame.quit()
