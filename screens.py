import pygame
class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = (18, 184, 255)
        self.hover_color = (23, 153, 209)
        self.is_hovered = False
        self.button_font = pygame.font.SysFont('Arial', 30)
        
    def draw(self, surface):
        # Draw button with hover effect
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
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        
    def is_clicked(self, pos, click):
        return self.rect.collidepoint(pos) and click
