import pygame
import os
from config import *

class DesignPlanBackground:
    def __init__(self):
        self.image = pygame.transform.smoothscale(
            pygame.image.load(
                os.path.join("Images", "Backgrounds", "design_plan_background.png")
            ).convert_alpha(),
            (SCREEN_WIDTH, SCREEN_HEIGHT)
        )

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
