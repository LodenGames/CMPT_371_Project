import socket
import pygame
import sys
import json
from constants import *
from screens import StartScreen, EndScreen, MainMenu
 

def recieve_player_info(client):
    data = client.recv(RECV_SIZE).decode()
    #take the (id, color, score) for each player
    players_json = json.loads(data)
    new_players = []
    for p in players_json:
        new_players.append((p[0], p[1], p[2]))
    return new_players


def receive_board_state(client):
    #for handling multiple packets since board state can be large
    buffer = b''
    while True:
        chunk = client.recv(RECV_SIZE)
        if not chunk:
            break 
        buffer += chunk
        if b'\n' in buffer:
            break
    #remove the newline then return the json data
    json_str = buffer.decode().strip() 
    return json.loads(json_str)


def draw_header():
    #draw header background
    pygame.draw.rect(screen, (200,200,200), (0, 0, WIDTH, HEADER_HEIGHT))
    pygame.draw.line(screen, BLACK, (0, HEADER_HEIGHT), (WIDTH, HEADER_HEIGHT), 2)
    
    #draw players info
    player_x_pos = 20
    for player in players:
        player_id, color, score = player
        
        player_text = f"Player {player_id}: {score}"
        if player_id == client_id:
            player_text += " (You)"
            
        text = font.render(player_text, True, color)
        text_rect = text.get_rect(topleft=(player_x_pos, 15))
        
        #small color indicator box next to player info
        pygame.draw.rect(screen, color, (player_x_pos - 15, 20, 10, 10))
        screen.blit(text, text_rect)
        
        #move to next player position
        player_x_pos += text_rect.width + 30

#draw board onto screen
def draw_board(board):
    #fill board white
    pygame.draw.rect(screen, WHITE, (0, HEADER_HEIGHT, WIDTH, BOARD_HEIGHT))
    
    #draw each square
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            square = board[row][col]
            
            # get the data from the square tuple
            if len(square) >= 5: 
                owner, color, being_drawn, drawer_id, drawer_color = square
            else: 
                owner, color = square
                being_drawn, drawer_id, drawer_color = False, None, None
                
            board_x = col * SQUARE_SIZE
            board_y = HEADER_HEIGHT + row * SQUARE_SIZE
            
            #draw colours
            if owner is not None:
                pygame.draw.rect(screen, color, (board_x, board_y, SQUARE_SIZE, SQUARE_SIZE))
            else:
                pygame.draw.rect(screen, WHITE, (board_x, board_y, SQUARE_SIZE, SQUARE_SIZE))
                
            #if someone else is drawing on a square indicate with transparent square colour
            if being_drawn and drawer_id != client_id:
                
                #draw transparanet surface
                transparent_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                drawer_rgba = (drawer_color[0], drawer_color[1], drawer_color[2], 90)
                transparent_surface.fill(drawer_rgba)

                screen.blit(transparent_surface, (board_x, board_y))
            
            #border drawing of square
            pygame.draw.rect(screen, BLACK, (board_x, board_y, SQUARE_SIZE, SQUARE_SIZE), 1)
    
    #if client drawing then draw the pixels
    if current_square and drawing:
        row, col = current_square
        # Find the player's color based on client_id
        player_color = None
        for player in players:
            if player[0] == client_id:
                player_color = player[1] 
                break
        
        # If player_color wasn't found for some reason, fallback to PLAYER_COLORS index
        if player_color is None:
            player_color = PLAYER_COLORS[(client_id - 1) % len(PLAYER_COLORS)]
            
        for x, y in square_pixels:
            screen_x = col * SQUARE_SIZE + x
            screen_y = HEADER_HEIGHT + row * SQUARE_SIZE + y
            screen.set_at((screen_x, screen_y), player_color)
    

#initializing pygame and its properties
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(f"Deny and Conquer")

pygame.font.init()
font = pygame.font.SysFont('Arial', 20)

clock = pygame.time.Clock()

#drawing state variables
current_square = None  #(row, col) of the square being drawn
drawing = False  
square_pixels = set()  #pixels drawn in the square

players = [] # list of (id, color, score) 

current_game_state = GAME_STATE_START
start_screen = StartScreen(WIDTH, HEIGHT) 
end_screen = EndScreen(WIDTH, HEIGHT)  
winners = []


board_state = [] #2d list of (Owner, color, being_drawn, drawer_id, drawer_color) 
#initial board state before game starts
for i in range(GRID_SIZE):  
    row = []
    for j in range(GRID_SIZE): 
        square = (None, WHITE)
        row.append(square) 
    board_state.append(row)  

menu_screen = MainMenu(WIDTH, HEIGHT)
ip_text = ""
start = True
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#loop for connecting screen only
while start:
    menu_screen.draw(screen)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        ip_text = menu_screen.handle_event(event)
        if ip_text != None:
            try :
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.settimeout(0.5)
                client.connect((ip_text, 50000))
                start = False

                break
            except Exception as e:
                print(f'Error {e}')
                menu_screen.error_connecting()
                print(ip_text)
                
                pass
    pygame.display.flip()
        
print(client.recv(RECV_SIZE).decode())

client.send("get_players".encode())
players = recieve_player_info(client)

client.send("get_id".encode())
client_id = int(client.recv(RECV_SIZE).decode())

#main game loop
running = True
while running:

    #request player and board state at start of each loop
    client.send("get_players".encode())
    players = recieve_player_info(client)

    # Check game status
    client.send("get_status".encode())
    status = client.recv(RECV_SIZE).decode()
    
    if status == "waiting" and current_game_state != GAME_STATE_START:
        current_game_state = GAME_STATE_START
    elif status == "playing" and current_game_state == GAME_STATE_START:
        current_game_state = GAME_STATE_PLAYING
    elif status == "game_over" and current_game_state != GAME_STATE_OVER:
        current_game_state = GAME_STATE_OVER
        # Get winners information
        client.send("get_winners".encode())
        winners = recieve_player_info(client)

    # Handle different game states
    if current_game_state == GAME_STATE_START:
        # Draw start screen
        start_screen.draw(screen, players, client_id)
        
        # Handle events for start screen
        for event in pygame.event.get():
            pos = pygame.mouse.get_pos()
            if event.type == pygame.QUIT:
                running = False
                client.send("exit".encode())
                break
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_screen.start_button.is_clicked(pos, True):
                    # Send start game command to server
                    client.send("start_game".encode())
                    response = client.recv(RECV_SIZE).decode()
                    print(f"Start game response: {response}")
    
    elif current_game_state == GAME_STATE_OVER:
        # Get the board state for background
        client.send("board".encode())
        board_state = receive_board_state(client)
        
        # Draw game over screen
        draw_header()
        draw_board(board_state)
        end_screen.draw_game_over_screen(screen, winners, client_id)
        
        # Handle events for game over screen
        for event in pygame.event.get():
            pos = pygame.mouse.get_pos()
            if event.type == pygame.QUIT:
                running = False
                client.send("exit".encode())
                break
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if end_screen.exit_button.is_clicked(pos, True):
                    running = False
                    client.send("exit".encode())
    
    else:  # GAME_STATE_PLAYING
        client.send("board".encode())
        board_state = receive_board_state(client)
        
        # Draw board and header
        draw_header()
        draw_board(board_state)
        
        # Handle gameplay events
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
                        response = client.recv(RECV_SIZE).decode("utf-8")
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
                print(client.recv(RECV_SIZE).decode("utf-8"))         
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
print(client.recv(RECV_SIZE).decode())
client.close()
pygame.quit()
sys.exit()