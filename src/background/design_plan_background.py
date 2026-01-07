import pygame
import os
from config import *

class DesignPlanBackground:
    def __init__(self):
        image_path = os.path.join(PROJECT_ROOT, "Images", "Backgrounds", "design_plan_background.png")
        if os.path.exists(image_path):
            raw_image = pygame.image.load(image_path).convert_alpha()
        else:
            print(f"Lỗi: Không tìm thấy ảnh tại {image_path}")
            raw_image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

        self.image = pygame.transform.smoothscale(raw_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

        self.x = SCREEN_WIDTH
        self.target_x = 0
        self.speed = 30
        self.done = False

    def update(self):
        if not self.done:
            self.x -= self.speed
            if self.x <= self.target_x:
                self.x = self.target_x
                self.done = True

    def draw(self, screen):
        screen.blit(self.image, (self.x, 0))
