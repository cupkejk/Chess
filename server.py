import socket
import threading
from chess import Board, Move
from random import choice
HOST = 'localhost'
PORT = 65432
logging = False

clients = []
colors = []
available_colors = [-1, 1]


board = Board()

def data_to_arr(data):
    message = data.decode('utf-8')
    message = message.split(' ')
    message = [eval(num) for num in message]
    return message

def move_to_data(move):
    message = "1 " + str(move.fromx) + " " + str(move.fromy) + " " + str(move.tox) + " " + str(move.toy)
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
        if message[0] == 1:
            move = Move(message[1], message[2], message[3], message[4])
            printLog("created a move")
            if board.isOccupied(move.fromx, move.fromy) == colors[playerid] and board.move_piece(move):
                printLog("made a move")
                data = move_to_data(move)
                printLog("sending data")
                clients[0].send(data)
                clients[1].send(data)






with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()

    while len(clients) < 2:
        conn, addr = s.accept()
        clients.append(conn)
        chosen_color = choice(available_colors)
        available_colors.remove(chosen_color)
        colors.append(chosen_color)
        threading.Thread(target=handle_client, args=(conn, addr, len(clients)-1)).start()