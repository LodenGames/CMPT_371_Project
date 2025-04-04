import socket
import json
import sys
import threading
from constants import *
from gamestate import Gamestate
from models import Player

if (len(sys.argv) == 2):
    HOST = sys.argv[1]
else:
    raise Exception ("Please provide 1 command line argument containing the server IP Address\n python server.py 192.168.0.1")

# Global game state
game_state = Gamestate()
player_id_counter = 1
game_over = False
waiting = True
available_ids = []

# Mutexes
game_state_lock = threading.Lock()
game_status_lock = threading.Lock()
player_counter_lock = threading.Lock()


# Function for each individual client thread
def handle_client(client_socket, player_id):

    global waiting, game_over

    # prevent server from crashing unecessarily
    try:

        # lock game state so only one thread has access
        with (game_state_lock):
            # create a new player with client socket and unique player_id
            new_player = Player(client_socket, player_id)
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
                            client_socket.send("Someone Else is Drawing on that square (Mutex Lock)".encode())
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
                            success = game_state.board.board[x][y].claim(new_player.id, new_player.color)
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
                    for player in game_state.players:
                        # store ID, color, score
                        player_list.append((player.id, player.color, player.score))
                # send data to client
                players_json = json.dumps(player_list)
                client_socket.send(players_json.encode())

            # client is exiting the game
            elif (command[0] == "exit"):

                # lock the game and modify player list
                with (game_state_lock):
                    # remove player from game if its not over
                    if (not game_over):
                        game_state.remove_player(new_player)
                # notify client exit was succesful
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
                # remove player from game state
                game_state.remove_player(new_player)
                # make their ID useable again
                with (player_counter_lock):
                    available_ids.append(player_id)
                    available_ids.sort()
            except:
                pass

        # try to close the socket
        try:
            client_socket.close()
        except:
            pass

# create tcp server socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# avoid "address already in use" when restarting server
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Flag to control server loop
server_running = True
# Function to handle server shutdown
def shutdown_server():
    global server_running
    print("Initiating server shutdown...")
    
    # tell all clients about shutdown
    with (game_state_lock):
        for player in game_state.players:
            try:
                player.client_socket.send("server_shutdown".encode())
            except:
                pass
    # change flag to false
    server_running = False
    print("Server shutdown complete.")

# Thread function to monitor console commands
def monitor_console():

    global server_running
    
    while (server_running):
        # get command from console
        cmd = input()

        # if command is kill
        if (cmd.lower() == "kill"):
            shutdown_server()
            break
        
        # if command is status
        elif (cmd.lower() == "status"):
            # lock game state
            with (game_state_lock):
                # print number of active players
                print(f"Active players: {len(game_state.players)}")
                # print each player's ID and score
                for player in game_state.players:
                    print(f"Player {player.id} (score: {player.score})")

        # if command is help
        elif (cmd.lower() == "help"):
            # print available commands
            print("Available commands:")
            print("  kill - Shut down the server")
            print("  status - Show connected players")
            print("  help - Show this help message")

        # if command is something else
        else:
            print(f"{cmd} is not valid... Please try again.")

# bind and listen for client connections
try:
    # bind server to set IP address and port number
    server.bind((HOST, PORT))
    # listen for connections
    server.listen(MAX_CLIENTS)
    print(f"Server started on {HOST} : {PORT}")
    # print initial message
    print("Available commands:")
    print("  kill - Shut down the server")
    print("  status - Show connected players and their scores")
    print("  help - Show this help message")


    # Start console monitoring thread to read from console and exec commands
    console_thread = threading.Thread(target=monitor_console)
    console_thread.daemon = True
    console_thread.start()

    # main server loop for handling new connections
    while (server_running):

        # Set a timeout so we can check if server_running changed
        server.settimeout(1.0)
        try:
            # accept a new connection, return new socket into client_socket
            client_socket, address = server.accept()
            print(f"Connection from {address}")

            # Check if we already have MAX_CLIENTS (4) clients connected
            with (game_state_lock):
                # if 4 connected tell client to try again later
                if len(game_state.players) >= MAX_CLIENTS:
                    print(f"Rejected connection from {address}: Maximum number of players ({MAX_CLIENTS}) reached")
                    client_socket.send("Server full. Try again later.".encode())
                    client_socket.close()
                    continue

            # lock player counter 
            with (player_counter_lock):
                # if a player disconnected use that ID
                if available_ids:
                    # reuse the lowest available ID
                    current_player_id = available_ids.pop(0)
                else:
                    # assign a new ID if none to reuse
                    current_player_id = player_id_counter
                    player_id_counter += 1
            
            # create new thread for each client
            # assign handle_client as the thread func ptr and assign args to handle_client
            client_thread = threading.Thread(target=handle_client, args=(client_socket, current_player_id))
            # automatically exit thread when program ends
            client_thread.daemon = True
            # start the client thread
            client_thread.start()

        except socket.timeout:
            # check if server_running flag still good
            continue
    
        except Exception as e:
            if server_running:
                print(f"Error accepting connection: {e}")

except KeyboardInterrupt:
    # if user uses Ctrl+C
    shutdown_server()

except Exception as e:
    # handle unexpected errors
    print(f"Server error: {e}")

finally:
    # clean up and close the server socket
    try:
        server.close()
    except:
        pass
