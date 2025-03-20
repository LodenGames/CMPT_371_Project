import pygame
from menu import Button

# Constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (230, 230, 230)
GREEN = (0, 200, 0)

#class just for the text input box
class TextInput:
    def __init__(self, x, y, width, height, default_text=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = default_text
        self.active = False
        self.font = pygame.font.SysFont('Arial', 24)
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_blink_speed = 500
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        
        #active when able to type
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.active = False
            else:
                if event.unicode in "0123456789.":
                    self.text += event.unicode
            return True
        return False
    
    def update(self, dt):
        #for cursor blinking
        self.cursor_timer += dt
        if self.cursor_timer >= self.cursor_blink_speed:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
    
    def draw(self, surface):
        # Draw the input box
        pygame.draw.rect(surface, LIGHT_GRAY, self.rect, 2, border_radius=10)
        pygame.draw.rect(surface, (0, 128, 255), self.rect, 2, border_radius=10)
        
        # Draw text
        text_surface = self.font.render(self.text, True, BLACK)
        # Center text vertically, align left with padding
        text_x = self.rect.x + 10
        text_y = self.rect.y + (self.rect.height - text_surface.get_height()) // 2
        surface.blit(text_surface, (text_x, text_y))
        
        # Draw cursor when active
        if self.active and self.cursor_visible:
            cursor_x = text_x + text_surface.get_width() + 2
            cursor_top = text_y
            cursor_bottom = text_y + text_surface.get_height()
            pygame.draw.line(surface, BLACK, (cursor_x, cursor_top), (cursor_x, cursor_bottom), 2)

#connection screen class
class ConnectionMenu:
    def __init__(self, screen_width, screen_height):
        self.width = screen_width
        self.height = screen_height
        self.title_font = pygame.font.SysFont('Arial', 40, bold=True)
        self.info_font = pygame.font.SysFont('Arial', 26)
        self.status_font = pygame.font.SysFont('Arial', 28)
        self.ip_font = pygame.font.SysFont('Arial', 32, bold=True)
        
        center_x = screen_width // 2
        
        input_width = 300
        input_height = 50
        self.ip_input = TextInput(center_x - input_width // 2,screen_height // 2 - 25,
                                  input_width,input_height,"127.0.0.1")
        

        self.host_ip = "127.0.0.1"  
        
        # Create buttons
        button_width = 200
        self.action_button = Button(center_x - button_width // 2,screen_height // 2 + 80, "Connect")
        self.back_button = Button(50, 50, "Back")

        self.mode = None  
        self.connected_players = 0
        self.max_players = 4
        self.status = "Not connected"
        self.is_connected = False
        self.waiting_for_host = False
    
    def set_mode(self, mode):
        self.mode = mode
        if mode == "host":
            self.action_button.text = "Start Game"
            self.status = "Waiting for players..."
        else:  # join
            self.action_button.text = "Connect"
            self.status = "Enter host IP address"
    
    def update(self, events, dt):
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False
        
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_click = True
            
            #text box activation
            if self.mode == "join":
                self.ip_input.handle_event(event)
        
        #button hover effects
        if self.mode == "join":
            self.ip_input.update(dt)
        self.action_button.check_hover(mouse_pos)
        self.back_button.check_hover(mouse_pos)
        
        # Check button clicks
        if self.back_button.is_clicked(mouse_pos, mouse_click):
            return "back"
            
        if self.action_button.is_clicked(mouse_pos, mouse_click):
            if self.mode == "host":
                self.status = "Game starting"
                self.action_button.text = "Starting"
                return "start_game"
            else:  # join
                self.is_connected = True
                self.waiting_for_host = True
                self.status = "Connected! Waiting for host to start..."
                self.action_button.text = "Waiting..."
                return "wait_for_host"
                
        return None
    
    def draw(self, surface):
        # Draw title based on mode
        if self.mode == "host":
            title_text = self.title_font.render("Host Game", True, BLACK)
        else: 
            title_text = self.title_font.render("Join Game", True, BLACK)
            
        title_rect = title_text.get_rect(center=(self.width // 2, 120))
        surface.blit(title_text, title_rect)
        
        #instructions text
        if self.mode == "host":
            info_text = self.info_font.render("Your IP Address:", True, BLACK)
        else:  
            info_text = self.info_font.render("Enter Host IP Address:", True, BLACK)
            
        info_rect = info_text.get_rect(center=(self.width // 2, self.height // 2 - 80))
        surface.blit(info_text, info_rect)

        # Draw IP address input box
        if self.mode == "host":
            ip_text = self.ip_font.render(self.host_ip, True, BLACK)
            ip_rect = ip_text.get_rect(center=(self.width // 2, self.height // 2 - 25))
            surface.blit(ip_text, ip_rect)
        else:  
            #draw input box for joining player
            self.ip_input.draw(surface)
        
        # Draw player count status
        if self.mode == "host":
            player_text = self.info_font.render(f"Players: {self.connected_players}/{self.max_players}", True, BLACK)
            player_rect = player_text.get_rect(center=(self.width // 2, self.height // 2 + 40))
            surface.blit(player_text, player_rect)
    
        # Draw buttons
        self.action_button.draw(surface)
        self.back_button.draw(surface)
    
    # for testing
    def add_player(self):
        if self.mode == "host" and self.connected_players < self.max_players:
            self.connected_players += 1
            return True
        return False
