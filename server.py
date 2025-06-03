import socket
import threading
from chess import Board, Move
from random import choice
import time
import random
HOST = 'localhost'
PORT = 65432
logging = True

clients = []
colors = []
available_colors = [-1, 1]


board = Board()
board_lock = threading.Lock()

pending_moves = []
pending_lock = threading.Lock()

def data_to_arr(data):
    message = data.decode('utf-8')
    message = message.split(' ')
    message = [eval(num) for num in message]
    return message

def move_to_data(move, stamina):
    message = "1 " + str(move.fromx) + " " + str(move.fromy) + " " + str(move.tox) + " " + str(move.toy) + " " + str(stamina)
    data = message.encode('utf-8')
    return data

def printLog(log):
    if logging:
        print("DEBUG INFO:", log)

def handle_client(conn, addr, playerid):
    while len(clients) < 2: pass
    data = str(colors[playerid]).encode('utf-8')
    conn.send(data)
    data = conn.recv(4)
    num = int.from_bytes(data)
    if num != 1: exit(0)
    
    while True:
        data = conn.recv(1024)
        if not data: break
        message = data_to_arr(data)
        printLog(f"received message: {message}")
        with board_lock:
            board.updateStamina()
        if message[0] == 1:
            move = Move(message[1], message[2], message[3], message[4])
            with pending_lock:
                pending_moves.append((playerid, move))

            time.sleep(0.05)

            with pending_lock:
                if len(pending_moves) > 1:
                    random.shuffle(pending_moves)

                for pid, mv in pending_moves:
                    with board_lock:
                        if board.isOccupied(mv.fromx, mv.fromy) == colors[pid] and board.move_piece(mv):
                            board.deductStamina(mv)
                            staminas = [board.getStamina(colors[0]), board.getStamina(colors[1])]
                            datas = [move_to_data(mv, staminas[0]), move_to_data(mv, staminas[1])]
                            clients[0].send(datas[0])
                            clients[1].send(datas[1])

                pending_moves.clear()







with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    printLog("Starting a server")

    while len(clients) < 2:
        conn, addr = s.accept()
        clients.append(conn)
        chosen_color = choice(available_colors)
        available_colors.remove(chosen_color)
        colors.append(chosen_color)
        threading.Thread(target=handle_client, args=(conn, addr, len(clients)-1)).start()
    
