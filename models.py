from constants import *

class Square:
    def __init__(self):
        self.owner = None #id of player who has claimed this square
        self.color = WHITE #color of the square
        self.claimed = False 
        self.being_drawn = False  #true when someone is currently drawing on this square
        self.drawer_id = None  #id of player currently drawing
        self.drawer_color = None  #color of player currently drawing

    #returns true if player has claimed this square
    def claim(self, player_id, color):
        if not self.claimed:
            self.owner = player_id
            self.color = color
            self.claimed = True
            return True
        return False

    #returns true if player has started drawing on this square
    def start_drawing(self, player_id, color):
        if not self.claimed and not self.being_drawn:
            self.being_drawn = True
            self.drawer_id = player_id
            self.drawer_color = color
            return True
        return False
    
    #returns true if player has stopped drawing on this square
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

    #convert board to a format that can be serialized to JSON
    def get_board_state(self):
    
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
        self.color = PLAYER_COLORS[(id - 1) % len(PLAYER_COLORS)]