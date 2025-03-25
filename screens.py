import pygame
from constants import *

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
        self.current_color = self.hover_color if self.is_hovered else self.color
    
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
        title_font = pygame.font.SysFont('Arial', 48, bold=True)
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
        
        # Draw popup background
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 3) #black border
        
        #sraw title
        title_font = pygame.font.SysFont('Arial', 48, bold=True)
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
