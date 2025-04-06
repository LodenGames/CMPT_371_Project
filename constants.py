WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (128, 255, 0)
BLUE = (0, 150, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
PLAYER_COLORS = [RED, GREEN, BLUE, YELLOW, PURPLE]
GRID_SIZE = 8
SQUARE_SIZE = 100

#screen dimensions
HEADER_HEIGHT = 50  #height of the top bar
BOARD_HEIGHT = SQUARE_SIZE * GRID_SIZE
WIDTH = SQUARE_SIZE * GRID_SIZE
HEIGHT = BOARD_HEIGHT + HEADER_HEIGHT
RECV_SIZE = 4096

#for drawing 
BRUSH_SIZE = 5  #Radius of the brush size when drawing
FILL_THRESHOLD = 0.5  

# Game states
GAME_STATE_START = 0    #start screen
GAME_STATE_PLAYING = 1  
GAME_STATE_OVER = 2   

# Game + server setup
SQUARES_NEEDED_TO_END_GAME = GRID_SIZE * GRID_SIZE
MAX_CLIENTS = 4
PORT = 50000