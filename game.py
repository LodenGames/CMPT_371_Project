import pygame

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
GRID_SIZE = 8
SQUARE_SIZE = SCREEN_WIDTH // GRID_SIZE
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)


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
            # Calculate the percentage filled
            percentage_filled = (self.filled_pixels / self.total_pixels) * 100 
            
            if percentage_filled >= 50:
                # Claim the square
                self.owner = self.scribbling_player
                self.color = self.scribbling_player.color
            else:
                # Reset the square
                self.square_surface.fill(WHITE)
                self.filled_pixels = 0
                
            self.being_scribbled = False
            self.scribbling_player = None
            
            return percentage_filled >= 50
        return False

    def point_in_square(self, pos):
        return (self.x <= pos[0] < self.x + self.width and
                self.y <= pos[1] < self.y + self.height)

    #put this into a method the position checker
    def draw_scribble(self, pos, color):
        if self.being_scribbled and self.point_in_square(pos):
            pygame.draw.circle(self.square_surface, color, 
                              (pos[0] - self.x, pos[1] - self.y), self.brushSize)
    
    def calculate_filled_pixels(self, color):
        # Count pixels that are not white
        self.filled_pixels = 0
        for x in range(self.width):
            for y in range(self.height):
                color = self.square_surface.get_at((x, y))  # Get (R, G, B, A) tuple
                if color[:3] != WHITE:  # Ignore alpha, compare only (R, G, B)
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

board = []
for row in range(GRID_SIZE):
            row_squares = []
            for col in range(GRID_SIZE):
                row_squares.append(Square(row, col))
            board.append(row_squares)

def draw(surface):
        for row in board:
            for square in row:
                square.draw(surface)

def get_square_at_position(pos):
        if pos[0] >= 0 and pos[0] < SCREEN_WIDTH and pos[1] >= 0 and pos[1] < SCREEN_HEIGHT:
            row = pos[1] // SQUARE_SIZE
            col = pos[0] // SQUARE_SIZE
            return board[row][col]
        return None

player1 = Player((255, 0, 0))  # Red

def update():
            global running
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                pos = pygame.mouse.get_pos()
                if get_square_at_position(pos) is None:
                    continue
                square = get_square_at_position(pos)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    print("Mouse Down")
                    square.start_scribble(player1)
                    player1.current_square = square
                elif event.type == pygame.MOUSEMOTION:
                    if pygame.mouse.get_pressed()[0]:  # Left button held
                         player1.current_square.sequence(pos, player1)
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                     player1.current_square.end_scribble()

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Deny and Conquer")
clock = pygame.time.Clock()
running = True


while running:
    screen.fill(WHITE)
    update()
    draw(screen)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()


