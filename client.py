import socket
import pygame
import sys
import json

WIDTH = 800
HEADER_HEIGHT = 50  #height of the top bar
BOARD_HEIGHT = 800  
HEIGHT = HEADER_HEIGHT + BOARD_HEIGHT
GRID_SIZE = 8
SQUARE_SIZE = BOARD_HEIGHT // GRID_SIZE
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (128, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

PLAYER_COLORS = [RED, GREEN, BLUE, YELLOW]
BRUSH_SIZE = 5  #Radius of the brush size when drawing

#initializing pygame and its properties
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Deny and Conquer")

pygame.font.init()
font = pygame.font.SysFont('Arial', 20)

#Connect to the server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 44444))

#inital welcome message
print(client.recv(1024).decode())

#drawing state variables
current_square = None  
drawing = False  
square_pixels = set()  #pixels drawn in the square
FILL_THRESHOLD = 0.5  

players = []  


def recieve_player_info(client):
    global players
    data = client.recv(4096).decode()
    players_json = json.loads(data)
    new_players = []
    for p in players_json:
        new_players.append((p[0], p[1], p[2]))
    players = new_players 

def receive_board_state(client):
    data = client.recv(4096).decode()
    return json.loads(data)

def draw_header():
    # Draw header background
    #(240, 240, 240)
    pygame.draw.rect(screen, (200,200,200), (0, 0, WIDTH, HEADER_HEIGHT))
    pygame.draw.line(screen, BLACK, (0, HEADER_HEIGHT), (WIDTH, HEADER_HEIGHT), 2)
    
    # Draw player list - Simplified
    player_x_pos = 20
    for player in players:
        player_id, color, score = player
        
        # Simple player text with ID and score
        text = font.render(f"Player {player_id}: {score}", True, color)
        text_rect = text.get_rect(topleft=(player_x_pos, 15))
        
        # Small color indicator
        pygame.draw.rect(screen, color, (player_x_pos - 15, 20, 10, 10))
        
        # Draw text
        screen.blit(text, text_rect)
        
        # Move to next position
        player_x_pos += text_rect.width + 30

# Function to draw the game board
def draw_board(board):
    #fill board white
    pygame.draw.rect(screen, WHITE, (0, HEADER_HEIGHT, WIDTH, BOARD_HEIGHT))
    
    #draw each square
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            square = board[row][col]
            
            # Unpack the square data (now includes drawing status)
            if len(square) >= 5:  # New format with drawing info
                owner, color, being_drawn, drawer_id, drawer_color = square
            else:  # Old format compatibility
                owner, color = square
                being_drawn, drawer_id, drawer_color = False, None, None
                
            # Calculate position with header offset
            board_x = col * SQUARE_SIZE
            board_y = HEADER_HEIGHT + row * SQUARE_SIZE
            
            # Draw the base square color
            if owner is not None:
                pygame.draw.rect(screen, color, (board_x, board_y, SQUARE_SIZE, SQUARE_SIZE))
            else:
                pygame.draw.rect(screen, WHITE, (board_x, board_y, SQUARE_SIZE, SQUARE_SIZE))
                
            # If someone is drawing on the square indicate with half opacity
            if being_drawn and drawer_color is not None:
                # Create a transparent surface
                transparent_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                drawer_rgba = (drawer_color[0], drawer_color[1], drawer_color[2], 128)
                transparent_surface.fill(drawer_rgba)
                
                #draw the transparent surface
                screen.blit(transparent_surface, (board_x, board_y))
            
            # Draw square border
            pygame.draw.rect(screen, BLACK, (board_x, board_y, SQUARE_SIZE, SQUARE_SIZE), 1)
    
    #if client drawing then draw the pixels
    if current_square and drawing:
        row, col = current_square
        for x, y in square_pixels:
            # Convert local pixel coordinates to screen coordinates
            screen_x = col * SQUARE_SIZE + x
            screen_y = HEADER_HEIGHT + row * SQUARE_SIZE + y
            screen.set_at((screen_x, screen_y), PLAYER_COLORS[0])  #draw pixel
    
    pygame.display.flip()


#Main game loop

board_state = [] #2d list of (Owner, color, being_drawn, drawer_id, drawer_color) 

for i in range(GRID_SIZE):  
    row = []
    for j in range(GRID_SIZE): 
        current_square = (None, WHITE)
        row.append(current_square) 
    board_state.append(row)  



client.send("get_players".encode())
recieve_player_info(client)


running = True
while running:
    # Draw header and board
    draw_header()
    draw_board(board_state)
    

    client.send("get_players".encode())
    recieve_player_info(client)


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            client.send("exit".encode())
            break

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            
            # Check if click is in the game board area (not in header)
            if y > HEADER_HEIGHT:
                # Adjust y coordinate to account for header
                board_y = y - HEADER_HEIGHT
                
                # Calculate board row and column correctly
                col = x // SQUARE_SIZE
                row = board_y // SQUARE_SIZE
                
                # Make sure coordinates are within board bounds
                if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
                    print(f"Clicked at ({row}, {col})")
                    
                    # Notify server that we're starting to draw
                    client.send(f"start_drawing {row} {col}".encode())
                    response = client.recv(1024).decode("utf-8")
                    print(response)
                    if response == "success":
                        current_square = (row, col)
                        drawing = True
                        square_pixels.clear()

        elif event.type == pygame.MOUSEBUTTONUP and drawing:
            row, col = current_square

            message = f"stop_drawing {row} {col}"

            #calculate if claimed square
            total_pixels = SQUARE_SIZE * SQUARE_SIZE
            filled_pixels = len(square_pixels)
            fill_percentage = filled_pixels / total_pixels
            if fill_percentage >= FILL_THRESHOLD:
                message += f" claim"
            else:
                message += f" no_claim"
            client.send(message.encode())   
            print(client.recv(1024).decode("utf-8"))         
            #reset drawing state square
            drawing = False
            current_square = None
            square_pixels.clear()
        
            client.send("get_players".encode())
            players_json = recieve_player_info(client)
            client.send("board".encode())
            board_state = receive_board_state(client)
        
        elif event.type == pygame.MOUSEMOTION and drawing:
            x, y = pygame.mouse.get_pos()
            #drawing state changes is local only so no message sending

            board_y = y - HEADER_HEIGHT
            row, col = current_square
            
            # Check if the mouse is still within the current square
            current_col = x // SQUARE_SIZE
            current_row = board_y // SQUARE_SIZE
            if current_row == row and current_col == col:
                #get the relative coordinates for the square
                local_x = x - (col * SQUARE_SIZE)
                local_y = board_y - (row * SQUARE_SIZE)
                square_pixels.add((local_x, local_y))
                
                #add pixels in the brush size area
                for offset_x in range(-BRUSH_SIZE + 1, BRUSH_SIZE):
                    for offset_y in range(-BRUSH_SIZE + 1, BRUSH_SIZE):
                        pixel_x = local_x + offset_x
                        pixel_y = local_y + offset_y
                        if 0 <= pixel_x < SQUARE_SIZE and 0 <= pixel_y < SQUARE_SIZE:
                            square_pixels.add((pixel_x, pixel_y))


print(client.recv(1024).decode())
client.close()
pygame.quit()
sys.exit()