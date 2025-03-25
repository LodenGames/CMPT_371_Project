import socket
import json
from constants import *
from gamestate import Gamestate
from models import Player

SQUARES_NEEDED_TO_END_GAME = 5 #should be GRID_SIZE * GRID_SIZE

def handle_single_player(client_socket, player_id):
    global waiting
    new_player = Player(client_socket, player_id)
    game_state.add_player(new_player)
    player2 = Player(None, player_id + 1)
    player3 = Player(None, player_id + 2)
    player4 = Player(None, player_id + 3)
    game_state.add_player(player2) #added 2nd player for testing purposes
    game_state.add_player(player3) #added 3rd player for testing purposes
    game_state.add_player(player4) #added 4th player for testing purposes
    print(f"Player {new_player.id} joined with color {new_player.color}")
    client_socket.send(f"Welcome Player {new_player.id}!".encode())

    game_board = game_state.board  #get the board of the game state

    #testing purposes start
    game_board.board[0][0].start_drawing(player2.id, player2.color)
    game_board.board[1][1].claim(player2.id, player2.color)
    game_board.board[1][2].claim(player2.id, player2.color)
    player2.score = 2

    game_board.board[2][2].start_drawing(player3.id, player3.color)
    game_board.board[2][3].claim(player3.id, player3.color)
    player3.score = 1

    game_board.board[4][4].start_drawing(player4.id, player4.color)
    game_board.board[4][5].claim(player4.id, player4.color)
    player4.score = 1
    #testing end

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
                if waiting:
                    client_socket.send("waiting".encode())
                elif game_state.total_score == SQUARES_NEEDED_TO_END_GAME:
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

            elif command[0] == "start_game":
                waiting = False
                client_socket.send("Game started".encode())

        except Exception as e:
            print(f"Error: {e}")
            break

    print(f"Player {new_player.id} disconnected.")
    client_socket.close()

#start server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 50000))
server.listen()
game_state = Gamestate()  #initialize the game state for the server
player_id_counter = 1  
game_over = False
waiting = True

# accept connection
print("Server started")
client_socket, address = server.accept()
print(f"Connection from {address}")
handle_single_player(client_socket, player_id_counter)



