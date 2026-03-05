import pygame
import numpy as np


class Button:
    def __init__(self, x, y, w, h, text, color=(50, 50, 60)):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.base_color = color
        self.active_color = (80, 80, 100)
        self.timer = 0
        
    def press(self):
        self.timer = 5

    def draw(self, screen, font):
        color = self.active_color if self.timer > 0 else self.base_color
        if self.timer > 0: self.timer -= 1
        
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, (100, 100, 110), self.rect, 2, border_radius=5)
        txt = font.render(self.text, True, (200, 200, 210))
        screen.blit(txt, (self.rect.centerx - txt.get_width()//2, 
                          self.rect.centery - txt.get_height()//2))


class PendulumRenderer:
    def __init__(self, width, height, scale):
        self.width = width
        self.height = height
        self.scale = scale
        self.offset = -100
        self.colors = {
            "BG": (15, 15, 20),
            "TRACK": (70, 70, 80),
            "LIMIT": (0, 180, 200),
            "CART": (230, 230, 235),
            "ROD": (255, 170, 60),
            "MASS": (100, 180, 255),
            "TEXT": (180, 180, 190),
            "RULER_MIN": (120, 120, 140, 40),
            "RULER_MAJ": (160, 160, 180, 90)
        }

    def _draw_ruler(self, screen, cart_y, track_limit, font):
        major_step = 0.1
        minor_step = 0.05
        center_x = self.width // 2
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # Draw Ticks
        x_val = -track_limit
        while x_val <= track_limit + 1e-6:
            px = center_x + int(x_val * self.scale)
            
            # Major ticks with labels
            if abs(x_val % major_step) < 1e-7 or abs(x_val % major_step - major_step) < 1e-7:
                pygame.draw.line(overlay, self.colors["RULER_MAJ"], (px, cart_y - 30), (px, cart_y + 30), 2)
                label = font.render(f"{x_val:.2f}", True, (150, 150, 170))
                overlay.blit(label, (px - 16, cart_y + 55))
            else:
                # Minor ticks
                pygame.draw.line(overlay, self.colors["RULER_MIN"], (px, cart_y - 20), (px, cart_y + 20), 1)
            
            x_val += minor_step
        
        screen.blit(overlay, (0, 0))

    def draw_world(self, screen, state, u, track_limit, L, speed, paused, mode_str, font, push_button):
        x, x_dot, theta, theta_dot = state
        screen.fill(self.colors["BG"])
        
        cart_y = self.height // 2 - self.offset
        cart_x = self.width // 2 + int(x * self.scale)
        
        # 1. Draw Ruler and Track
        self._draw_ruler(screen, cart_y, track_limit, font)
        
        left_limit = self.width // 2 - int(track_limit * self.scale)
        right_limit = self.width // 2 + int(track_limit * self.scale)
        
        pygame.draw.line(screen, self.colors["TRACK"], (left_limit, cart_y), (right_limit, cart_y), 4)
        pygame.draw.line(screen, self.colors["LIMIT"], (left_limit, cart_y+40), (left_limit, cart_y-40), 3)
        pygame.draw.line(screen, self.colors["LIMIT"], (right_limit, cart_y+40), (right_limit, cart_y-40), 3)

        # 2. Draw Cart
        cart_w = int(0.067 * self.scale)
        cart_h = int(0.05 * self.scale)
        cart_rect = pygame.Rect(cart_x - cart_w//2, cart_y - cart_h//2, cart_w, cart_h)
        pygame.draw.rect(screen, self.colors["CART"], cart_rect, border_radius=6)

        # 3. Draw Pendulum
        pend_x = cart_x - int(L * self.scale * np.sin(theta))
        pend_y = cart_y - int(L * self.scale * np.cos(theta))
        pygame.draw.line(screen, self.colors["ROD"], (cart_x, cart_y), (pend_x, pend_y), 6)
        pygame.draw.circle(screen, self.colors["MASS"], (pend_x, pend_y), 10)

        # 4. Draw HUD
        status = "PAUSED" if paused else "RUNNING"
        info = (f"{mode_str} | x={state[0]:.3f}  theta={state[2]:.3f}  "
                f"u={u:.2f}N  speed={speed:.2f}x  {status}")
        
        text_surface = font.render(info, True, self.colors["TEXT"])
        screen.blit(text_surface, (20, 20))

        # 5. Draw the Button
        push_button.draw(screen, font)
        
        text_surface = font.render(info, True, self.colors["TEXT"])
        screen.blit(text_surface, (20, 20))