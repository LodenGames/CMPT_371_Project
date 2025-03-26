import socket
import json
import threading
from constants import *
from gamestate import Gamestate
from models import Player


# Game + server setup
SQUARES_NEEDED_TO_END_GAME = GRID_SIZE * GRID_SIZE
MAX_CLIENTS = 4
HOST = "0.0.0.0"
PORT = 50000

# Global game state
game_state = Gamestate()
player_id_counter = 1
game_over = False
waiting = True

# Mutexes
game_state_lock = threading.lock()
game_status_lock = threading.lock()
player_counter_lock = threading.lock()

# Function for each individual client thread
def handle_client(client_socket, player_id):

    global waiting, game_over
    # prevent server from crashing unecessarily
    try:

        # lock game state so only one thread has access
        with (game_state_lock):
            # create a new player with client socket and unique player_id
            new_player = Player(client_socket, id)
            game_state.add_player(new_player)
            print(f"Player {new_player.id} joined with color {new_player.color}")
        # send a message to the player to let them know they've joined
        client_socket.send(f"Welcome Player {new_player.id}!".encode())

        # -- main loop for client/server communication --
        while (True):
            # receive msg from client
            data = client_socket.recv(1024).decode()
            # if msg is empty
            if (not data):
                break
            # split msg into list of commands 
            else:
                command = data.split()
            
            # --- handling the command ---
            
            # client wants current board state
            if (command[0] == "board"):
                
                # lock game state and access board data
                with (game_state_lock):
                    current_board_state = game_state.board.get_board_state()
                # send board state to client
                current_board_state_json = json.dumps(current_board_state)
                client_socket.send(current_board_state_json.encode())
            
            # client wants to draw on a square
            elif (command[0] == "start_drawing"):

                # get (x,y) coords from command
                x = int(command[1])
                y = int(command[2])
                # check coords are within valid grid range
                if (0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE):
                    # lock game state and modify board
                    with (game_state_lock):
                        # draw on the given square
                        success = game_state.board.board[x][y].start_drawing(new_player.id, new_player.color)
                        # if successful
                        if (success):
                            client_socket.send("success".encode())
                        # if not successful
                        else:
                            client_socket.send("failure to draw".encode())
                # coords were invalid
                else:
                    client_socket.send("Invalid coordinates".encode())

            # client wants to stop drawing
            elif (command[0] == "stop_drawing"):

                # get coords
                x = int(command[1])
                y = int(command[2])
                #  check coords in range
                if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
                    # lock game state
                    with (game_state_lock):
                        # check if succesful
                        success = game_state.board.board[x][y].stop_drawing(new_player.id)
                        # if player wants to claim this square
                        if command[3] == "claim":
                            # increase players score
                            game_state.add_score(new_player)
                            # attempt to claim square
                            success = game_state.board[x][y].claim(new_player.id, new_player.color)
                            # check if game over condition met
                            if game_state.total_score >= SQUARES_NEEDED_TO_END_GAME:
                                with (game_status_lock):
                                    game_over = True
                            # check if attempt to claim square was succesful
                            if success:
                                client_socket.send(f"claimed".encode())
                            else:
                                client_socket.send(f"claim failed".encode())
                        # player does not want to claim the square
                        elif command[3] == "no_claim":
                            client_socket.send(f"not_claimed".encode())

            # client requested the active list of players
            elif (command[0] == "get_players"):
                
                # lock game state and access data
                with (game_state_lock):
                    # access each player
                    player_list = []
                    for player in player_list:
                        # store ID, color, score
                        player_list.append(player.id, player.color, player.score)
                # send data to client
                players_json = json.dumps(player_list)
                client_socket.send(players_json.encode())

            # client is exiting the game
            elif (command[0] == "exit"):

                # lock the game and modify player list
                with (game_state_lock):
                    # remove player if game not over
                    if (not game_over):
                        game_state.remove_player(new_player)
                # notify client that they exited successfully and disconnect
                client_socket.send("Exit Success".encode())
                break

            # client requested their ID
            elif (command[0] == "get_id"):
                client_socket.send(str(new_player.id).encode())

            # client requested the game's status
            elif (command[0] == "get_status"):
                
                # set def status
                status = "playing"
                # lock game and check
                with (game_status_lock):
                    if (waiting):
                        status = "waiting"
                    elif (game_state.total_score >= SQUARES_NEEDED_TO_END_GAME):
                        status = "game_over"
                # send status to client
                client_socket.send(status.encode())

            # client requested list of winners
            elif (command[0] == "get_winners"):

                # lock game state
                with (game_state_lock):
                    # get highest score in the game
                    highest_score = game_state.get_highest_score()
                    # find players with highest score
                    player_list = []
                    for player in game_state.players:
                        if player.score == highest_score:
                            player_list.append((player.id, player.color, player.score))
                # send winners list to client
                players_json = json.dumps(player_list)
                client_socket.send(players_json.encode())

            # client wants to start the game
            elif (command[0] == "start_game"):
                
                # lock game state
                with (game_state_lock):
                    # change game status
                    waiting = False
                # tell client game has started
                client_socket.send("Game started".encode())
    
    # catch errors and print error msg
    except Exception as e:
        print(f"Error handling client {player_id}: {e}")
    
    # cleanup client as it disconnects
    finally:
        # print msg to tell that player has left
        print(f"Player {player_id} disconnected.")

        # try to remove player from game state securely
        with (game_state_lock):
            try:
                game_state.remove_player(new_player)
            except:
                pass

        # try to close the socket
        try:
            client_socket.close()
        except:
            pass
