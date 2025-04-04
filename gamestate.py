from models import GameBoard, Player, Square
from constants import *

class Gamestate:
    def __init__(self):
        self.board = GameBoard()  
        self.players = []  
        self.total_score = 0

    def add_player(self, Player):
        self.players.append(Player)


    def remove_player(self, Player):
        for row in self.board.board:
            for square in row:
                if square.owner == Player.id:
                    square.owner = None
                    square.color = WHITE
                    square.claimed = False
                    self.total_score -= 1
                
                if square.drawer_id == Player.id:
                    square.being_drawn = False
                    square.drawer_id = None
                    square.drawer_color = None
        
        Player.score = 0
        
        self.players.remove(Player)

    def add_score(self, Player):
        Player.score += 1
        self.total_score += 1

    def get_highest_score(self):
        highest_score = 0
        for player in self.players:
            if player.score > highest_score:
                highest_score = player.score
        return highest_score



