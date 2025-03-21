import pygame
import numpy as np

pygame.init()

ScreenWidth = 1200
ScreenHeight = 1200
numRows = 8
numCols = 8
SquareSize = ScreenWidth//numRows
playerColors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
brush_size = 5

#Create screen
screen = pygame.display.set_mode((ScreenWidth,ScreenHeight))
#2d array for our game grid
grid = np.full((numRows,numCols, 3), 255, dtype=np.uint8)
#2d array, will be used to keep track of squares that are busy
currentlyDrawing = np.full(((numRows),numCols), None)
#Keeps track of if the square is already colored in
coloredSquare = np.zeros((numRows, numCols), dtype=bool)
#Dictionary to keep track of number of squares each player has (the score)
playerScores = {i:0 for i in range(4)}
# Dictionary to keep track of number of colored pixels in each square
pixelCounts = {(row, col): 0 for row in range(numRows) for col in range(numCols)}

currentPlayer = 0
#TEMP buttons to simulate different players
buttonRects = []
for i in range(4):
    rect = pygame.Rect(i * (ScreenWidth // 4), ScreenHeight - 50, ScreenWidth // 4, 50)
    buttonRects.append(rect)

#Individual squares for  coloring
squareSurfaces = [[pygame.Surface((SquareSize, SquareSize)) for _ in range(numCols)] for _ in range(numRows)]
for row in range(numRows):
    for col in range(numCols):
        squareSurfaces[row][col].fill((255, 255, 255))

def draw_grid():
    for row in range(numRows):
        for col in range(numCols):
            screen.blit(squareSurfaces[row][col], (col * SquareSize, row * SquareSize))
            pygame.draw.rect(screen, (0, 0, 0), (col * SquareSize, row * SquareSize, SquareSize, SquareSize), 2)

#TEMP remove later. Buttons to simulate different players
def draw_buttons():
    font = pygame.font.Font(None, 36)
    for i, rect in enumerate(buttonRects):
        pygame.draw.rect(screen, playerColors[i], rect)
        text = font.render(f"P{i+1}", True, (0, 0, 0))
        screen.blit(text, (rect.x + 15, rect.y + 10))

#Used to keep track if player is already coloring a square, they cant go to another
#Probably have to change this for multiplayer
activeSquare = None

def color_square(pos):
    global activeSquare
    row = pos[1] // SquareSize
    col = pos[0] // SquareSize

    if activeSquare is None:
        activeSquare = (row, col)  
    
    if activeSquare != (row, col):
        return  
    
    #Check if the square is already colored in
    if coloredSquare[row][col]:
        return
    #If the square isnt busy then we can set it to the current player
    if currentlyDrawing[row][col] is None:
        currentlyDrawing[row][col] = currentPlayer

    if currentlyDrawing[row][col] == currentPlayer:
        local_x, local_y = pos[0] % SquareSize, pos[1] % SquareSize
        # circular brush to color more than 1 pixel
        for dx in range(-brush_size, brush_size + 1):
            for dy in range(-brush_size, brush_size + 1):
                if dx**2 + dy**2 <= brush_size**2: 
                    new_x, new_y = local_x + dx, local_y + dy
                    if 0 <= new_x < SquareSize and 0 <= new_y < SquareSize:
                        squareSurfaces[row][col].set_at((new_x, new_y), playerColors[currentPlayer])
                        pixelCounts[(row, col)] += 1

#Used to check if square is at 50%
def check_percentage():
    for row in range(numRows):
        for col in range(numRows):
            if currentlyDrawing[row][col] is not None and not coloredSquare[row][col]:
                #Count amount of non white pixels
                colored_pixels = sum(
                    1 for x in range(SquareSize) for y in range(SquareSize)
                    if squareSurfaces[row][col].get_at((x, y))[:3] != (255, 255, 255)
                )
                total_pixels = SquareSize * SquareSize
                # Check if 50% is colored and color it in if yes
                if colored_pixels >= total_pixels // 2:  
                    coloredSquare[row][col] = True 
                    squareSurfaces[row][col].fill(playerColors[currentlyDrawing[row][col]])
                    #Add to player score
                    playerScores[currentlyDrawing[row][col]] += 1 

                #Otherwise if the player didnt reach 50% reset the square
                else:
                    currentlyDrawing[row][col] = None  
                    #Make white again
                    squareSurfaces[row][col].fill((255, 255, 255)) 
                    #Remove stored pixels
                    pixelCounts[(row, col)] = 0  
running = True
mouse_down = False


#Check if all squares filled
def check_end_game():
    if np.all(coloredSquare):
        show_end_screen()
#End screen
def show_end_screen():
    screen.fill((0, 0, 0))  # Clear screen
    font = pygame.font.Font(None, 50)
    text = font.render("Game Over! Scores:", True, (255, 255, 255))
    screen.blit(text, (ScreenWidth // 4, ScreenHeight // 4))
    
    for i, score in playerScores.items():
        text = font.render(f"P{i+1}: {str(score)}", True, playerColors[i])
        screen.blit(text, (ScreenWidth // 4, ScreenHeight // 3 + i * 40))
    
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()


while running:
    screen.fill((0, 0, 0)) 
    draw_grid()
    draw_buttons()
    pygame.display.flip()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            if mouse_y >= ScreenHeight - 50:
                for i, rect in enumerate(buttonRects):
                    if rect.collidepoint(mouse_x, mouse_y):
                        currentPlayer = i  # Switch player
            else:
                mouse_down = True
        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_down = False
            activeSquare = None
            check_percentage()
            check_end_game()
        elif event.type == pygame.MOUSEMOTION and mouse_down:
            color_square(event.pos)       
            
pygame.quit()