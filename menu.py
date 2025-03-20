import pygame
from constants import *

button_8x8 = pygame.Rect(75, 200, 100, 50)
button_color = (0, 128, 255)
button_hover = (0, 119, 239)
button_height = 100
button_width = 175
class Button:
    def __init__(self, x, y, text):
        self.rect = pygame.Rect(x, y, button_width, button_height)
        self.text = text
        self.color = button_color
        self.hover_color = button_hover
        self.is_hovered = False
        
    def draw(self, surface, font):
        # Draw button with hover effect
        current_color = None
        if self.is_hovered:
            current_color = self.hover_color
        else:
            current_color = self.color
        pygame.draw.rect(surface, current_color, self.rect, border_radius=10)  # Button background
        
        # Render text
        text_surface = font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        
    def is_clicked(self, pos, click):
        return self.rect.collidepoint(pos) and click

class Menu:
    def __init__(self):
        self.title_font = pygame.font.SysFont('Arial', 50, bold=True)
        self.button_font = pygame.font.SysFont('Arial', 30)
        
        # Create buttons
        center_x = SCREEN_WIDTH // 2 - button_width // 2
        
        self.host_button = Button(center_x, SCREEN_HEIGHT // 2 - 100, "Host Game")
        self.join_button = Button(center_x, SCREEN_HEIGHT // 2 + 100, "Join Game")
    
    def update(self, events):
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False
        
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_click = True
        
        #check hover
        self.host_button.check_hover(mouse_pos)
        self.join_button.check_hover(mouse_pos)
        
        #check click
        if self.host_button.is_clicked(mouse_pos, mouse_click):
            return "host"
        elif self.join_button.is_clicked(mouse_pos, mouse_click):
            return "join"
            
        return None
    
    def draw(self, surface):
        # Draw title
        title_text = self.title_font.render("Deny and Conquer", True, BLACK)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        surface.blit(title_text, title_rect)
        
        # Draw buttons
        self.host_button.draw(surface, self.button_font)
        self.join_button.draw(surface, self.button_font)