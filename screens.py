import pygame
from constants import *

#GUI stuff

class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = (18, 184, 255)
        self.hover_color = (23, 153, 209)
        self.is_hovered = False
        self.button_font = pygame.font.SysFont('Arial', 30)
        
    def draw(self, surface):
        #select color based on hover
        current_color = None
        if self.is_hovered:
            current_color = self.hover_color
        else:
            current_color = self.color
        pygame.draw.rect(surface, current_color, self.rect, border_radius=10)  #button background
        
        #button text
        text_surface =  self.button_font.render(self.text, True, (0,0,0))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    
    #updates whether hovered
    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        if self.is_hovered:
            self.current_color = self.hover_color
        else:
            self.current_color = self.color
    
    def is_clicked(self, mouse_pos, check_hover=False):
        if check_hover:
            self.check_hover(mouse_pos)
        return self.rect.collidepoint(mouse_pos)

class StartScreen:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        # Create start button
        button_width, button_height = 200, 60
        button_x = (width - button_width) // 2
        button_y = height - 120
        self.start_button = Button(button_x, button_y, button_width, button_height, "START GAME")
        
        
    def draw(self, screen, players, client_id):
        
        screen.fill(WHITE)
        
        #draw title
        title_font = pygame.font.SysFont('Arial', 36, bold=True)
        title = title_font.render("Deny and Conquer", True, BLACK)
        title_rect = title.get_rect(center=(self.width // 2, 100))
        screen.blit(title, title_rect)
        
        #draw "players connected"
        subtitle_font = pygame.font.SysFont('Arial', 36)
        subtitle = subtitle_font.render("Players Connected:", True, BLACK)
        subtitle_rect = subtitle.get_rect(center=(self.width // 2, 180))  
        screen.blit(subtitle, subtitle_rect)
        
        #list players vertically
        player_y = 230
        for player in players:
            player_id, color, score = player
            message = f"Player {player_id}"
            if player_id == client_id:
                message += " (You)"
            player_font = pygame.font.SysFont('Arial', 24)
            player_text = player_font.render(message, True, color)
            player_rect = player_text.get_rect(center=(self.width // 2, player_y))
            screen.blit(player_text, player_rect)
            player_y += 40
        

        self.start_button.check_hover(pygame.mouse.get_pos())
        self.start_button.draw(screen)
    
class EndScreen:
    def __init__(self, width, height):
        self.total_width = width
        self.total_height = height

        #screen relative information
        self.width = self.total_width * 0.6
        self.height = self.total_height * 0.7
        self.x = (self.total_width - self.width) // 2
        self.y = (self.total_width - self.height) // 2

        #exit button
        button_width, button_height = 150, 50
        button_x = (self.total_width - button_width) // 2
        button_y = self.y + self.height - 80

        self.exit_button = Button(button_x, button_y, button_width, button_height, "EXIT")

    def draw_game_over_screen(self, screen, winners, client_id):    
        
        #draw background
        pygame.draw.rect(screen, WHITE, (self.x-50, self.y, self.width+100, self.height))
        pygame.draw.rect(screen, BLACK, (self.x-50, self.y, self.width+100, self.height), 3) #black border
        
        #sraw title
        title_font = pygame.font.SysFont('Arial', 36, bold=True)
        title = title_font.render("GAME OVER", True, BLACK)
        title_rect = title.get_rect(center=(self.total_width // 2, self.y + 50))
        screen.blit(title, title_rect)
        
        #draw winners list
        winners_y = self.y + 120
        win_text = "Winner"
        if len(winners) > 1:
            win_text = "Winners"

        
        tie_font = pygame.font.SysFont('Arial', 36)
        tie_text = tie_font.render(win_text, True, BLACK)
        tie_rect = tie_text.get_rect(center=(self.total_width // 2, winners_y))
        screen.blit(tie_text, tie_rect)
        
        #list all winners vertically
        winners_y += 60
        for winner in winners:
            winner_id, winner_color, winner_score = winner
            winner_font = pygame.font.SysFont('Arial', 24)
            message = f"Player {winner_id}: {winner_score} squares"
            if winner_id == client_id:
                message += " (You)"
            winner_text = winner_font.render(message, True, winner_color)
            winner_rect = winner_text.get_rect(center=(self.total_width // 2, winners_y))
            screen.blit(winner_text, winner_rect)
            winners_y += 40
        

        
        #draw button
        self.exit_button.check_hover(pygame.mouse.get_pos())    
        self.exit_button.draw(screen)

class MainMenu:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.host_input = "127.0.0.1"
        self.input_active = False #true when typing in box enabled
        self.error_connect = False
        self.error_host = ""
        
        #text box for input
        input_width = 300
        input_height = 40
        self.text_box = pygame.Rect((width - input_width) // 2, height // 2, input_width, input_height)
        
        # Create connect button
        button_width, button_height = 180, 60
        button_x = (width - button_width) // 2
        button_y = height // 2 + input_height + 30
        self.connect_button = Button(button_x, button_y, button_width, button_height, "CONNECT")
    
    def draw(self, screen):
        screen.fill(WHITE)
        
        #draw title
        title_font = pygame.font.SysFont('Arial', 36, bold=True)
        title = title_font.render("Deny and Conquer", True, BLACK)
        title_rect = title.get_rect(center=(self.width // 2, 50))
        screen.blit(title, title_rect)
        
        #draw message
        subtitle_font = pygame.font.SysFont('Arial', 30)
        subtitle = subtitle_font.render("Join Host", True, BLACK)
        subtitle_rect = subtitle.get_rect(center=(self.width // 2, self.height // 2 - 50))
        screen.blit(subtitle, subtitle_rect)
        
        #draw text box
        if self.input_active:
            border_color = (18, 184, 255)
        else:
            border_color = BLACK
        pygame.draw.rect(screen, WHITE, self.text_box)
        pygame.draw.rect(screen, border_color, self.text_box, 2) #draw border
        
        #draw the text
        input_font = pygame.font.SysFont('Arial', 24)
        input_text = input_font.render(self.host_input, True, BLACK)
        text_rect = input_text.get_rect(midleft=(self.text_box.left + 10, self.text_box.centery))
        screen.blit(input_text, text_rect)
        
        #draw connect button
        self.connect_button.check_hover(pygame.mouse.get_pos())
        self.connect_button.draw(screen)
        
        #draw instruction message
        instr_font = pygame.font.SysFont('Arial', 16)
        instr_text = instr_font.render("Enter server IP address of HOST", True, BLACK)
        instr_rect = instr_text.get_rect(center=(self.width // 2, self.height // 2 - 15))
        screen.blit(instr_text, instr_rect)

        # draw connect error message
        subtitle_font = pygame.font.SysFont('Arial', 30)
        if self.error_connect:
            subtitle = subtitle_font.render(f"No Server at {self.error_host}", True, RED)
        else:
            subtitle = subtitle_font.render("", True, BLACK)
        subtitle_rect = subtitle.get_rect(center=(self.width // 2, self.height // 2 - 100))
        screen.blit(subtitle, subtitle_rect)

    def error_connecting(self):
        self.error_connect = True
        self.error_host = self.host_input

    def handle_event(self, event):
        #handle events
        if event.type == pygame.MOUSEBUTTONDOWN:
            #check clicked on text box
            self.input_active = self.text_box.collidepoint(event.pos)
            
            #check if click connected button
            if self.connect_button.is_clicked(event.pos, True):
                return self.host_input
        
        # handle kegboard
        if event.type == pygame.KEYDOWN and self.input_active:
            if event.key == pygame.K_RETURN:
                self.input_active = False
            elif event.key == pygame.K_BACKSPACE:
                self.host_input = self.host_input[:-1] 
            else:
                
                if len(self.host_input) < 30:  
                    self.host_input += event.unicode
        
        return None 
