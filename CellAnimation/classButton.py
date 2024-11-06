import pygame

button_color = (100, 100, 255)
button_hover_color = (150, 150, 255)
text_color = (255, 255, 255)

# Button class to manage buttons
class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.Font(None, 24)

    def draw(self, surface, hover=False):
        color = button_hover_color if hover else button_color
        pygame.draw.rect(surface, color, self.rect)
        text_surface = self.font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)