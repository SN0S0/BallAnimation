import pygame

slider_color = (200, 200, 200)
slider_handle_color = (0, 0, 0)
WHITE = (255, 255, 255)


# Slider class to manage each slider
class Slider:
    def __init__(self, x, y, width, label, min_val, max_val, default_val):
        self.rect = pygame.Rect(x, y, width, 10)
        self.min_val = min_val
        self.max_val = max_val
        self.value = default_val
        self.label = label
        self.handle_x = x + int((default_val - min_val) / (max_val - min_val) * width)

    def update(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.handle_x = max(self.rect.left, min(self.rect.right, mouse_pos[0]))
            self.value = self.min_val + (self.handle_x - self.rect.left) / self.rect.width * (self.max_val - self.min_val)

    def draw(self, surface):
        pygame.draw.rect(surface, slider_color, self.rect)
        pygame.draw.circle(surface, slider_handle_color, (self.handle_x, self.rect.centery), 8)
        font = pygame.font.Font(None, 24)
        label_text = f"{self.label}: {self.value:.2f}"
        label_surface = font.render(label_text, True, WHITE)
        surface.blit(label_surface, (self.rect.left, self.rect.top - 30))
