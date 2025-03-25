from models import GameBoard, Player, Square
class Gamestate:
    def __init__(self):
        self.board = GameBoard()  
        self.players = []  
        self.total_score = 0

    def add_player(self, Player):
        self.players.append(Player)


    def remove_player(self, Player):
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



