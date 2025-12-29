import pygame
import math
import os
from config import *

class AssembleZone:
    def __init__(self):
        self.rect = pygame.Rect(0, 0, 400, 400) # Kích thước vùng hiển thị
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        
        self.image = None
        self.current_state = None
        
        # Biến đếm thời gian rung lắc
        self.teeter_timer = 0

    def set_state(self, new_state, robot_id):
        self.current_state = new_state
        # Đường dẫn ảnh: Images/Robot_1/head_body.png ...
        path = os.path.join(PROJECT_ROOT, "Images", robot_id, f"{new_state}.png")
        
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            # Scale ảnh vừa khung
            self.image = pygame.transform.smoothscale(img, (self.rect.width, self.rect.height))
        else:
            print(f"Missing image: {path}")

    def wrong_animation(self):
        self.teeter_timer = 30 # Rung trong 30 frames (khoảng 0.5 giây)

    def draw(self, surface):
        draw_x = self.rect.x
        draw_y = self.rect.y

        # --- LOGIC RUNG LẮC (TEETER) ---
        if self.teeter_timer > 0:
            # Tạo độ lệch x ngẫu nhiên hoặc theo hàm sin
            offset = math.sin(self.teeter_timer * 0.5) * 10 # Rung biên độ 10 pixel
            draw_x += offset
            self.teeter_timer -= 1

        # Vẽ ảnh
        if self.image:
            surface.blit(self.image, (draw_x, draw_y))
        else:
            # Placeholder nếu chưa có ảnh
            pygame.draw.rect(surface, (0, 255, 0), (draw_x, draw_y, self.rect.width, self.rect.height), 2)