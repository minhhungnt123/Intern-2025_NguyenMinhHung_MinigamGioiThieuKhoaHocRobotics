import pygame
import os
from config import *

class AssembleZone:
    def __init__(self):
        # Vùng va chạm
        self.rect = pygame.Rect(0, 0, 260, 260)
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        self.image = None
        self.current_state = None
        self.robot_id = None
        self.teeter_time = 0

    def set_state(self, new_state, robot_id):
        self.current_state = new_state
        self.robot_id = robot_id
        ROBOT_SIZES = {
            "robot_1": (450, 450),
            "robot_2": (480, 480),
            "default": (260, 260) 
        }
        img_path = os.path.join(
            PROJECT_ROOT,
            "Images",
            robot_id,
            f"{new_state}.png"
        )

        if os.path.exists(img_path):
            raw_img = pygame.image.load(img_path).convert_alpha()
            target_size = ROBOT_SIZES.get(robot_id, ROBOT_SIZES["default"])
            self.image = pygame.transform.smoothscale(raw_img, target_size)
            self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            
        else:
            print(f"❌ Thiếu ảnh trạng thái: {img_path}")
            self.image = None

    def wrong_animation(self):
        self.teeter_time = 25

    def draw(self, screen):
        # Hiệu ứng rung lắc khi sai
        offset_x = 0
        if self.teeter_time > 0:
            offset_x = (-1) ** self.teeter_time * 6
            self.teeter_time -= 1

        # Vẽ ảnh tại vị trí rung lắc
        draw_rect = self.rect.copy()
        draw_rect.x += offset_x

        if self.image:
            screen.blit(self.image, draw_rect)
        else:
            # Vẽ khung giữ chỗ nếu chưa có ảnh
            pygame.draw.rect(screen, (180, 180, 255), draw_rect, border_radius=12)
            pygame.draw.rect(screen, (120, 120, 200), draw_rect, 3, border_radius=12)