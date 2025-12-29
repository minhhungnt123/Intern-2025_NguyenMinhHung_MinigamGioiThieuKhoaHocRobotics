import pygame
import os
from config import PROJECT_ROOT

class DragItem:
    def __init__(self, name, pos, robot_id):
        self.name = name
        self.start_pos = pos
        self.dragging = False

        # --- FIX: Ensure correct folder name ---
        # Force robot_id to match folder name if needed
        # (Only use this if your folder is definitely "Robot_1")
        if robot_id == "robot_1": 
            robot_id = "Robot_1"

        img_path = os.path.join(
            PROJECT_ROOT,
            "Images",
            robot_id,      # Ensure this is "Robot_1"
            f"{name}.png"
        )
        
        # Debug: Print path to console
        print(f"Loading Part: {name} at {img_path}")

        if os.path.exists(img_path):
            self.image = pygame.image.load(img_path).convert_alpha()
        else:
            print(f"❌ Error: Cannot find image for {name}!")
            # Create a RED SQUARE if image is missing so you can see the position
            self.image = pygame.Surface((80, 80))
            self.image.fill((255, 0, 0)) # Red

        self.rect = self.image.get_rect(topleft=pos)
        self.offset = (0, 0) # Initialize offset

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.dragging = True
                mx, my = event.pos
                self.offset = (self.rect.x - mx, self.rect.y - my)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                mx, my = event.pos
                self.rect.x = mx + self.offset[0]
                self.rect.y = my + self.offset[1]

    def reset(self):
        self.rect.topleft = self.start_pos

    def draw(self, surface):
        surface.blit(self.image, self.rect)