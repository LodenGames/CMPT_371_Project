from models import GameBoard, Player, Square
class Gamestate:
    def __init__(self):
        self.board = GameBoard()  
        self.players = []  

    def add_player(self, Player):
        self.players.append(Player)


    def remove_player(self, Player):
        self.players.remove(Player)
        



