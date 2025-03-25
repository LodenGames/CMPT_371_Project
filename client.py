import socket
import pygame
import sys
import json
from constants import *
from screens import Button

#screen dimensions
HEADER_HEIGHT = 50  #height of the top bar
BOARD_HEIGHT = SQUARE_SIZE * GRID_SIZE
WIDTH = SQUARE_SIZE * GRID_SIZE
HEIGHT = BOARD_HEIGHT + HEADER_HEIGHT

#for drawing 
BRUSH_SIZE = 5  #Radius of the brush size when drawing
FILL_THRESHOLD = 0.5  

def recieve_player_info(client):
    data = client.recv(4096).decode()
    players_json = json.loads(data)
    new_players = []
    for p in players_json:
        new_players.append((p[0], p[1], p[2]))
    return new_players

def receive_board_state(client):
    data = client.recv(4096).decode()
    return json.loads(data)

def draw_header():
    # Draw header background
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
                
            # If someone else is drawing on the square indicate with half opacity
            if being_drawn and drawer_id != client_id:
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
    

def draw_game_over_screen(winners):    
    # Draw the game over rectangle
    global exit_button
    g_over_width = WIDTH * 0.6
    g_over_height = HEIGHT * 0.7
    g_over_x = (WIDTH - g_over_width) // 2
    g_over_y = (HEIGHT - g_over_height) // 2
    
    # Draw popup background
    pygame.draw.rect(screen, WHITE, (g_over_x, g_over_y, g_over_width, g_over_height))
    pygame.draw.rect(screen, BLACK, (g_over_x, g_over_y, g_over_width, g_over_height), 3) #black border
    
    # Draw "GAME OVER" title
    title_font = pygame.font.SysFont('Arial', 48, bold=True)
    title = title_font.render("GAME OVER", True, BLACK)
    title_rect = title.get_rect(center=(WIDTH // 2, g_over_y + 50))
    screen.blit(title, title_rect)
    
    # Draw winners list
    winners_y = g_over_y + 120
    win_text = "Winner"
    if len(winners) > 1:
        win_text = "Winners"

    
    tie_font = pygame.font.SysFont('Arial', 36)
    tie_text = tie_font.render(win_text, True, BLACK)
    tie_rect = tie_text.get_rect(center=(WIDTH // 2, winners_y))
    screen.blit(tie_text, tie_rect)
    
    # List all winners vertically
    winners_y += 60
    for winner in winners:
        winner_id, winner_color, winner_score = winner
        winner_font = pygame.font.SysFont('Arial', 24)
        winner_text = winner_font.render(f"Player {winner_id}: {winner_score} squares", True, winner_color)
        winner_rect = winner_text.get_rect(center=(WIDTH // 2, winners_y))
        screen.blit(winner_text, winner_rect)
        winners_y += 40
    
    # Draw exit button
    button_width, button_height = 150, 50
    button_x = (WIDTH - button_width) // 2
    button_y = g_over_y + g_over_height - 80

    exit_button = Button(button_x, button_y, button_width, button_height, "EXIT")
    
    # Button colors based on hover
    exit_button.check_hover(pygame.mouse.get_pos())    
    exit_button.draw(screen)



def receive_winners(client):
    data = client.recv(4096).decode()
    return json.loads(data)

#initializing pygame and its properties
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Deny and Conquer")

pygame.font.init()
font = pygame.font.SysFont('Arial', 20)

clock = pygame.time.Clock()

#Connect to the server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 44444))

#inital welcome message
print(client.recv(1024).decode())

#drawing state variables
current_square = None  
drawing = False  
square_pixels = set()  #pixels drawn in the square


players = [] # list of (id, color, score) 
exit_button = Button(0, 0, 0, 0, "")

#Main game loop

board_state = [] #2d list of (Owner, color, being_drawn, drawer_id, drawer_color) 

for i in range(GRID_SIZE):  
    row = []
    for j in range(GRID_SIZE): 
        current_square = (None, WHITE)
        row.append(current_square) 
    board_state.append(row)  


client.send("get_players".encode())
players = recieve_player_info(client)

client.send("get_id".encode())
client_id = int(client.recv(1024).decode())


running = True
game_over = False
winners = []

while running:

    #request player and board state at start of each loop
    client.send("get_players".encode())
    players = recieve_player_info(client)

    client.send("board".encode())
    board_state = receive_board_state(client)

    # Check game status
    client.send("get_status".encode())
    status = client.recv(1024).decode()
    
    if status == "game_over" and not game_over:
        game_over = True
        #get winners information
        client.send("get_winners".encode())
        winners = receive_winners(client)
    

    if game_over:
        #draw board in background
        draw_header()
        draw_board(board_state)
        
        #draw end game screen on top of background
        draw_game_over_screen(winners)
        
        #event handling
        for event in pygame.event.get():
            pos = pygame.mouse.get_pos()
            if event.type == pygame.QUIT:
                running = False
                client.send("exit".encode())
                break
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if exit_button.is_clicked(pos, True):
                    running = False
                    client.send("exit".encode())
    else:
        #draw board and header
        draw_header()
        draw_board(board_state)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                client.send("exit".encode())
                break

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                
                if y > HEADER_HEIGHT:
                
                    board_y = y - HEADER_HEIGHT
                    col = x // SQUARE_SIZE
                    row = board_y // SQUARE_SIZE
                    if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
                        print(f"Clicked at ({row}, {col})")
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
            

            
            elif event.type == pygame.MOUSEMOTION and drawing:
                x, y = pygame.mouse.get_pos()
                #drawing state changes is local only so no message sending

                board_y = y - HEADER_HEIGHT
                row, col = current_square
                
                # check if the mouse is still within the current square
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
    pygame.display.flip()
    clock.tick(60) #set max fps to 60

#exit message before quiting
print(client.recv(1024).decode())
client.close()
pygame.quit()
sys.exit()