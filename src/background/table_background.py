import os
import pygame
import math
from config import *

class TableBackground:
    def __init__(self):
        try:
            path = os.path.join(PROJECT_ROOT, "Images", "Backgrounds", "table_background.png")
            
            self.image = pygame.transform.smoothscale(
                pygame.image.load(path).convert(),
                (SCREEN_WIDTH + 40, SCREEN_HEIGHT + 40)
            )
        except Exception as e:
            print("⚠ Background load error:", e)
            self.image = pygame.Surface((SCREEN_WIDTH + 40, SCREEN_HEIGHT + 40))
            self.image.fill((200, 200, 200))

        # Thời gian cho parallax
        self.time = 0.0

        # Độ mạnh
        self.amp_x = 5
        self.amp_y = 2

        # Tốc độ
        self.speed_x = 0.6
        self.speed_y = 0.4

    def update(self):
        # Tăng thời gian
        self.time += 0.1

        # Tính offset bằng sin / cos
        self.offset_x = math.sin(self.time * self.speed_x) * self.amp_x
        self.offset_y = math.cos(self.time * self.speed_y) * self.amp_y

    def draw(self, screen):
        # Vẽ background với offset
        screen.blit(
            self.image,
            (-20 + self.offset_x, -20 + self.offset_y)
        )
