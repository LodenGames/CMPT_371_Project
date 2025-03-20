import pygame
from menu import Menu
from connection_menu import ConnectionMenu
from constants import *

#game state
STATE_MENU = 0
STATE_CONNECTION = 1
STATE_GAME = 2


class Square:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        #global x,y coordinates
        self.x = col * SQUARE_SIZE
        self.y = row * SQUARE_SIZE
        self.width = SQUARE_SIZE
        self.height = SQUARE_SIZE
        self.owner = None
        self.color = WHITE
        self.brushSize = 5
        self.square_surface = pygame.Surface((self.width, self.height))
        self.square_surface.fill(WHITE)
        self.being_scribbled = False
        self.scribbling_player = None
        self.filled_pixels = 0
        self.total_pixels = self.width * self.height

    def start_scribble(self, player):
        if not self.being_scribbled and self.owner is None:
            self.being_scribbled = True
            self.scribbling_player = player
            return True
        return False

    def end_scribble(self):
        if self.being_scribbled:
            #Calculate how filled the square is
            percentage_filled = (self.filled_pixels / self.total_pixels) * 100 
            
            if percentage_filled >= 50:
                #claim square
                self.owner = self.scribbling_player
                self.color = self.scribbling_player.color
            else:
                #reset square if not filled enough
                self.square_surface.fill(WHITE)
                self.filled_pixels = 0
                
            self.being_scribbled = False
            self.scribbling_player = None
            
            return percentage_filled >= 50
        return False

    def point_in_square(self, pos):
        return (self.x <= pos[0] < self.x + self.width and
                self.y <= pos[1] < self.y + self.height)


    def draw_scribble(self, pos, color):
        if self.being_scribbled and self.point_in_square(pos):
            #draw relative to the square's position
            pygame.draw.circle(self.square_surface, color, 
                              (pos[0] - self.x, pos[1] - self.y), self.brushSize)
    
    def calculate_filled_pixels(self, color):
        # Count pixels that are not white
        self.filled_pixels = 0
        for x in range(self.width):
            for y in range(self.height):
                color = self.square_surface.get_at((x, y))  # Get rgb color of pixel
                if color[:3] != WHITE:  #compare only rgb 
                    self.filled_pixels += 1
        print(self.filled_pixels) #for debugging 

    def draw(self, surface):
        # Draw the base square
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height)) 
        pygame.draw.rect(surface, BLACK, (self.x, self.y, self.width, self.height), 1) #border of square
        
        # draw the square when being painted
        if self.being_scribbled or self.owner is None:
            surface.blit(self.square_surface, (self.x, self.y))
            pygame.draw.rect(surface, BLACK, (self.x, self.y, self.width, self.height), 1)
    
    def sequence(self, pos, player):
         if not self.point_in_square(pos):
            return
         if self.being_scribbled: 
            self.draw_scribble(pos, player.color)
            self.calculate_filled_pixels(player.color)


class Player:
    def __init__(self, color):
        self.color = color
        self.current_square = None
        self.score = 0

board = []
for row in range(GRID_SIZE):
        row_squares = []
        for col in range(GRID_SIZE):
            row_squares.append(Square(row, col))
        board.append(row_squares)

def draw_game(surface):
        for row in board:
            for square in row:
                square.draw(surface)

def get_square_at_position(pos):
        if pos[0] >= 0 and pos[0] < SCREEN_WIDTH and pos[1] >= 0 and pos[1] < SCREEN_HEIGHT:
            row = pos[1] // SQUARE_SIZE
            col = pos[0] // SQUARE_SIZE
            return board[row][col]
        return None

player1 = Player(RED)  # Red
player2 = Player(BLUE)  # Blue 

def update_game(events):
        for event in events:
            pos = pygame.mouse.get_pos()
            square = get_square_at_position(pos)
            if square is None:
                continue
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                print("Mouse Down")
                square.start_scribble(player1)
                player1.current_square = square
            elif event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed()[0]:  # Left button held
                    if player1.current_square is not None:
                        player1.current_square.sequence(pos, player1)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if player1.current_square is not None:
                    player1.current_square.end_scribble()
                    if player1.current_square.owner is not None:
                        player1.score += 1
                    player1.current_square = None

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Deny and Conquer")
clock = pygame.time.Clock()
running = True

# Menu and game state
game_state = STATE_MENU
menu = Menu()
connection_menu = ConnectionMenu(SCREEN_WIDTH, SCREEN_HEIGHT)

#game loop
while running:
    dt = clock.tick(60)  # Delta time in milliseconds
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
    
    screen.fill(WHITE)
    
    if game_state == STATE_MENU:
        action = menu.update(events)
        menu.draw(screen)
        if action == "host":
            game_state = STATE_CONNECTION
            connection_menu.set_mode("host")
            print("Opening host setup...")
        elif action == "join":
            game_state = STATE_CONNECTION
            connection_menu.set_mode("join")
            print("Opening join setup...")
            
    elif game_state == STATE_CONNECTION:
        action = connection_menu.update(events, dt)
        connection_menu.draw(screen)
        if action == "back":
            game_state = STATE_MENU
        elif action == "start_game" or action == "wait_for_host":
            if action == "start_game":
                print("Starting game as host...")
            else:
                print("Waiting for host to start game...")
            game_state = STATE_GAME
            
    elif game_state == STATE_GAME:
        update_game(events)
        draw_game(screen)
    
    #draw surface into screen
    pygame.display.flip()

pygame.quit()


