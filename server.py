import socket
import json

WHITE = (255, 255, 255)
BLACK = (0,   0,   0)
RED = (255,   0,   0)
GREEN = (128, 255,   0)
BLUE = (0,   0, 255)
YELLOW = (255, 255,   0)

GRID_SIZE = 8
SQUARE_SIZE = 100  
colors = [RED, GREEN, BLUE, YELLOW]

class Square:
    def __init__(self):
        self.owner = None #id of player who has claimed this square
        self.color = WHITE #color of the square
        self.claimed = False 
        self.being_drawn = False  #true when someone is currently drawing on this square
        self.drawer_id = None  #id of player currently drawing
        self.drawer_color = None  #color of player currently drawing

    def claim(self, player_id, color):
        if not self.claimed:
            self.owner = player_id
            self.color = color
            self.claimed = True
            return True
        return False

    def start_drawing(self, player_id, color):
        if not self.claimed and not self.being_drawn:
            self.being_drawn = True
            self.drawer_id = player_id
            self.drawer_color = color
            return True
        return False
    
    def stop_drawing(self, player_id):
        if self.being_drawn and self.drawer_id == player_id:
            self.being_drawn = False
            self.drawer_id = None
            self.drawer_color = None
            return True
        return False

class GameBoard:
    def __init__(self):
        self.board = []  
        for i in range(GRID_SIZE):
            row = []  
            for j in range(GRID_SIZE):
                row.append(Square())  
            self.board.append(row)  

    def get_board_state(self):
        #convert board to a format that can be serialized to JSON
        board_state = []
        for row in self.board:
            row_state = []
            for square in row:
                # each square is (owner, color, being_drawn, drawer_id, drawer_color)
                row_state.append((
                    square.owner, 
                    square.color, 
                    square.being_drawn, 
                    square.drawer_id, 
                    square.drawer_color
                ))
            board_state.append(row_state)
        return board_state

class Player:
    def __init__(self, client_socket, id):
        self.client_socket = client_socket
        self.score = 0
        self.id = id
        self.color = colors[(id - 1) % len(colors)]

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 44444))
server.listen()

player_id_counter = 1  
players = []  

def handle_single_player(client_socket, player_id):
    new_player = Player(client_socket, player_id)
    players.append(new_player)
    players.append(Player(None, player_id + 1)) #testing purposes
    print(f"Player {new_player.id} joined with color {new_player.color}")
    client_socket.send(f"Welcome Player {new_player.id}!".encode())

    game_board = GameBoard()  # Initialize the game board for this session

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
                        new_player.score += 1
                        sucess = game_board.board[x][y].claim(new_player.id, new_player.color)
                        if success:
                            client_socket.send(f"claimed".encode())
                        else:
                            client_socket.send(f"claim failed".encode())
                    elif command[3] == "no_claim":
                        client_socket.send(f"not_claimed".encode())

            elif command[0] == "get_players":
                # Send list of players in (id, color, score)
                player_list = []
                for p in players:
                    player_list.append((p.id, p.color, p.score))
                players_json = json.dumps(player_list)
                client_socket.send(players_json.encode())

            elif command[0] == "exit":
                players.remove(new_player)
                client_socket.send("Exit accepted".encode())
                break

        except Exception as e:
            print(f"Error: {e}")
            break

    print(f"Player {new_player.id} disconnected.")
    client_socket.close()

# accept connection
print("Server started")
client_socket, address = server.accept()
print(f"Connection from {address}")
handle_single_player(client_socket, player_id_counter)



