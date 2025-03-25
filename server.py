import socket
import json
from constants import *
from gamestate import Gamestate
from models import Player

def handle_single_player(client_socket, player_id):
    new_player = Player(client_socket, player_id)
    game_state.add_player(new_player)
    game_state.add_player(Player(None, player_id + 1)) #added 2nd player for testing purposes
    print(f"Player {new_player.id} joined with color {new_player.color}")
    client_socket.send(f"Welcome Player {new_player.id}!".encode())

    game_board = game_state.board  #get the board of the game state

    while True:
        try:
            #recieve message
            data = client_socket.recv(1024).decode()
            if not data:
                break  #client disconnected

            command = data.split()

            if command[0] == "board":
                #send board state to the client
                board_state = game_board.get_board_state()
                board_state_json = json.dumps(board_state)
                client_socket.send(board_state_json.encode())

            elif command[0] == "start_drawing":
                x, y = int(command[1]), int(command[2])
                if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
                    #check if able to draw on selected square
                    success = game_board.board[x][y].start_drawing(new_player.id, new_player.color)
                    if success:
                        client_socket.send(f"success".encode())
                    else:
                        client_socket.send(f"fail".encode())
                else:
                    client_socket.send("Invalid coordinates".encode())
            
            elif command[0] == "stop_drawing":
                x, y = int(command[1]), int(command[2])
                if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
                    success = game_board.board[x][y].stop_drawing(new_player.id)
                    if command[3] == "claim":
                        game_state.add_score(new_player)
                        success = game_board.board[x][y].claim(new_player.id, new_player.color)
                        if success:
                            client_socket.send(f"claimed".encode())
                        else:
                            client_socket.send(f"claim failed".encode())
                    elif command[3] == "no_claim":
                        client_socket.send(f"not_claimed".encode())

            elif command[0] == "get_players":
                # Send list of players in (id, color, score)
                player_list = []
                for p in game_state.players:
                    player_list.append((p.id, p.color, p.score))
                players_json = json.dumps(player_list)
                client_socket.send(players_json.encode())

            elif command[0] == "exit":
                if not game_over:
                    game_state.remove_player(new_player)
                client_socket.send("Exit accepted".encode())
                break
            
            elif command[0] == "get_id":
                client_socket.send(str(new_player.id).encode())
            
            elif command[0] == "get_status":
                if game_state.total_score == 1:
                    game_over = True
                    client_socket.send("game_over".encode())
                else:
                    client_socket.send("playing".encode())
            elif command[0] == "get_winners":
                highest_score = game_state.get_highest_score()
                player_list = []
                for p in game_state.players:
                    if p.score == highest_score:
                        player_list.append((p.id, p.color, p.score))
                players_json = json.dumps(player_list)
                client_socket.send(players_json.encode())

        except Exception as e:
            print(f"Error: {e}")
            break

    print(f"Player {new_player.id} disconnected.")
    client_socket.close()

#start server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 44444))
server.listen()
game_state = Gamestate()  #initialize the game state for the server
player_id_counter = 1  
game_over = False

# accept connection
print("Server started")
client_socket, address = server.accept()
print(f"Connection from {address}")
handle_single_player(client_socket, player_id_counter)



