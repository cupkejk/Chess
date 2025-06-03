import socket
import threading
import time
import random
from chess import Board, Move

HOST = 'localhost'
PORT = 65432
LOGGING_ENABLED = True


clients_sockets = []
player_colors = []
available_colors = [-1, 1]

board = Board()
board_lock = threading.Lock()

intentions = {0: None, 1: None}
intentions_lock = threading.Lock()
CONFLICT_WINDOW = 0.25


def data_to_arr(data_bytes):
    message_str = data_bytes.decode('utf-8')
    parts = message_str.split(' ')
    return [eval(num_str) for num_str in parts]

def move_to_data(move_obj):
    message = f"1 {move_obj.fromx} {move_obj.fromy} {move_obj.tox} {move_obj.toy}"
    return message.encode('utf-8')

def print_log(log_message):
    if LOGGING_ENABLED:
        print(f"SERVER LOG: {log_message}")

def broadcast(data_bytes):
    print_log(f"Broadcasting: {data_bytes.decode('utf-8') if isinstance(data_bytes, bytes) else data_bytes}")
    for client_socket in list(clients_sockets):
        if client_socket:
            try:
                client_socket.sendall(data_bytes)
            except socket.error as e:
                print_log(f"Error broadcasting to a client: {e}. Client might have disconnected.")
                try:
                    idx = clients_sockets.index(client_socket)
                    clients_sockets[idx] = None
                except ValueError:
                    pass

def handle_client(conn, addr, playerid):
    print_log(f"Player {playerid} connected from {addr}, assigned color {player_colors[playerid]}")

    try:
        color_data = str(player_colors[playerid]).encode('utf-8')
        conn.sendall(color_data)
        ack = conn.recv(4)
        if not ack or int.from_bytes(ack) != 1:
            print_log(f"Player {playerid} failed to acknowledge color. Closing connection.")
            return
    except (socket.error, ConnectionResetError) as e:
        print_log(f"Socket error during initial setup for Player {playerid}: {e}")
        return
    except ValueError:
        print_log(f"Invalid ack from Player {playerid}. Closing connection.")
        return


    while True:
        try:
            raw_data = conn.recv(1024)
            if not raw_data:
                print_log(f"Player {playerid} disconnected (received no data).")
                break

            message_arr = data_to_arr(raw_data)
            print_log(f"Player {playerid} (Color {player_colors[playerid]}) sent: {message_arr}")

            if message_arr[0] == 1:
                received_move = Move(message_arr[1], message_arr[2], message_arr[3], message_arr[4])
                current_time = time.time()
                other_playerid = 1 - playerid
                
                action_taken_in_conflict = False
                data_to_broadcast_after_resolution = None

                with intentions_lock:
                    other_player_intent_obj = intentions[other_playerid]

                    if other_player_intent_obj and \
                       (current_time - other_player_intent_obj['timestamp'] < CONFLICT_WINDOW) and \
                       received_move.tox == other_player_intent_obj['move'].tox and \
                       received_move.toy == other_player_intent_obj['move'].toy:
                        
                        action_taken_in_conflict = True
                        print_log(f"CONFLICT DETECTED: P{playerid} ({received_move}) vs "
                                  f"P{other_playerid} ({other_player_intent_obj['move']}) "
                                  f"for square ({received_move.tox},{received_move.toy})")

                        # These intents are now "consumed" for this conflict resolution
                        current_move_info = {'move': received_move, 'playerid': playerid, 'data': raw_data}
                        other_move_info = {'move': other_player_intent_obj['move'], 
                                           'playerid': other_playerid, 
                                           'data': other_player_intent_obj['original_data']}
                        
                        intentions[playerid] = None # Clear current player's pending intent if any (unlikely path, but safe)
                        intentions[other_playerid] = None # Clear other player's conflicting intent

                        # --- Resolve Conflict (needs board access) ---
                        with board_lock:
                            contenders = []
                            # Check if current player's move originates from their piece
                            if board.isOccupied(current_move_info['move'].fromx, current_move_info['move'].fromy) == player_colors[current_move_info['playerid']]:
                                contenders.append(current_move_info)
                            else:
                                print_log(f"Conflict: P{current_move_info['playerid']}'s move {current_move_info['move']} invalid at origin.")
                            
                            # Check if other player's (conflicting) move originates from their piece
                            if board.isOccupied(other_move_info['move'].fromx, other_move_info['move'].fromy) == player_colors[other_move_info['playerid']]:
                                contenders.append(other_move_info)
                            else:
                                print_log(f"Conflict: P{other_move_info['playerid']}'s move {other_move_info['move']} invalid at origin.")

                            if not contenders:
                                print_log("Conflict Resolution: No valid contenders (both moves invalid at origin).")
                            elif len(contenders) == 1:
                                winner_info = contenders[0]
                                print_log(f"Conflict Resolution: One valid contender. Winner P{winner_info['playerid']}.")
                                if board.move_piece(winner_info['move']): # move_piece also does chess rule validation
                                    data_to_broadcast_after_resolution = winner_info['data']
                                else:
                                    print_log(f"Conflict Winner P{winner_info['playerid']}'s move {winner_info['move']} failed board.move_piece().")
                            else: # Both moves originated validly, so coin toss
                                winner_info = random.choice(contenders)
                                print_log(f"Conflict Resolution: Coin toss. Winner P{winner_info['playerid']}.")
                                if board.move_piece(winner_info['move']):
                                    data_to_broadcast_after_resolution = winner_info['data']
                                else:
                                    print_log(f"Conflict Coin Toss Winner P{winner_info['playerid']}'s move {winner_info['move']} failed board.move_piece().")
                # End of intentions_lock for the conflict check block

                if not action_taken_in_conflict:
                    # --- NO CONFLICT / SEQUENTIAL MOVE PATH ---
                    move_was_successful_sequentially = False
                    with board_lock:
                        # Validate origin and attempt the move
                        if board.isOccupied(received_move.fromx, received_move.fromy) == player_colors[playerid] and \
                           board.move_piece(received_move):
                            data_to_broadcast_after_resolution = raw_data # This move is the one to broadcast
                            move_was_successful_sequentially = True
                        else:
                            print_log(f"Sequential Path: P{playerid}'s move {received_move} was invalid or failed board.move_piece().")
                            # TODO: Optionally send an "invalid move" message back to only this client
                    
                    if move_was_successful_sequentially:
                        # If the move was successful, it becomes this player's new "intent"
                        with intentions_lock:
                             intentions[playerid] = {'move': received_move, 
                                                     'timestamp': current_time, 
                                                     'original_data': raw_data,
                                                     'playerid': playerid
                                                    }
                
                if data_to_broadcast_after_resolution:
                    broadcast(data_to_broadcast_after_resolution)

                # Consider checking for game over (checkmate/stalemate) after any successful move
                # with board_lock:
                #     winner_status = board.checkWin() # Assuming this method exists
                # if winner_status != 0: # 0 = ongoing, 1 = white wins, -1 = black wins, 2 = draw
                #     broadcast(f"GAMEOVER {winner_status}".encode('utf-8')) # Define protocol for game over
                #     print_log(f"Game Over! Status: {winner_status}")
                #     # Potentially break loops and close connections after a delay
                #     break 

        except (socket.error, ConnectionResetError) as e:
            print_log(f"Socket error for Player {playerid}: {e}. Closing connection.")
            break
        except Exception as e:
            print_log(f"Unexpected error in handle_client for Player {playerid}: {e}")
            import traceback
            traceback.print_exc()
            break
            
    print_log(f"Player {playerid} handler thread terminating.")
    if conn:
        conn.close()
    
    if playerid < len(clients_sockets):
        clients_sockets[playerid] = None 
    with intentions_lock:
        intentions[playerid] = None
    
    if all(cs is None for cs in clients_sockets) and len(clients_sockets) == 2:
        print_log("Both players disconnected. Server might stop if not designed for new games.")



if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        #s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print_log(f"Server listening on {HOST}:{PORT}")

        active_player_threads = []
        
        num_players = 0
        while num_players < 2:
            try:
                conn, addr = s.accept()
                
                playerid = num_players
                
                chosen_color = random.choice(available_colors)
                available_colors.remove(chosen_color)
                
                if playerid == 0:
                    clients_sockets = [None, None]
                    player_colors = [0, 0]

                clients_sockets[playerid] = conn
                player_colors[playerid] = chosen_color
                
                print_log(f"Accepted connection from {addr}. Assigned PlayerID {playerid}.")
                
                thread = threading.Thread(target=handle_client, args=(conn, addr, playerid))
                active_player_threads.append(thread)
                thread.start()
                num_players += 1
            except Exception as e:
                print_log(f"Error accepting connections: {e}")
                break

        if num_players == 2:
            print_log("Two players connected. Game is active.")
        else:
            print_log("Failed to get two players. Server might not function as expected.")

        for t in active_player_threads:
            t.join() 
            
        print_log("All client threads have finished. Server shutting down.")