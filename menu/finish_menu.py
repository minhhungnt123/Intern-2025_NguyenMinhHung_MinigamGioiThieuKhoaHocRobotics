import pygame
import os
import math
from config import *

class FinishMenu:
    def __init__(self, screen):
        self.screen = screen
        self.is_active = False
        self.start_time = 0
        self.show_buttons = False
        
        # --- 1. LOAD ASSETS ---
        # Ảnh chúc mừng
        congrats_path = os.path.join(PROJECT_ROOT, "Images", "Menu", "congratulation.png")
        if os.path.exists(congrats_path):
            raw_img = pygame.image.load(congrats_path).convert_alpha()
            
            # Chỉnh kích thước ảnh gốc
            target_width = 600  
            scale_factor = target_width / raw_img.get_width()
            target_height = int(raw_img.get_height() * scale_factor)
            
            self.congrats_img = pygame.transform.smoothscale(raw_img, (target_width, target_height))
        else:
            font = pygame.font.SysFont("Arial", 60, bold=True)
            self.congrats_img = font.render("CONGRATULATIONS!", True, (255, 215, 0))

        # Âm thanh chiến thắng
        self.win_sound = None
        self.sound_duration = 2000 
        sound_path = os.path.join(PROJECT_ROOT, "Sound", "winning.mp3")
        if os.path.exists(sound_path):
            try:
                self.win_sound = pygame.mixer.Sound(sound_path)
                self.sound_duration = self.win_sound.get_length() * 1000
            except: pass

        # --- 2. LOAD NÚT BẤM (THAY ĐỔI VỊ TRÍ DỌC) ---
        # Nút Restart: Nằm ở trên (cách tâm 80px xuống dưới)
        self.btn_restart_img, self.btn_restart_rect = self._load_button("restart_button.png", 0, 50)
        
        # Nút Home: Nằm ở dưới (cách tâm 180px xuống dưới -> cách nút trên 100px)
        self.btn_home_img, self.btn_home_rect = self._load_button("home.png", 0, 180)

        # Màn hình đen mờ
        self.dim_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.dim_surface.set_alpha(150) 
        self.dim_surface.fill((0, 0, 0))

    def _load_button(self, filename, x_offset, y_offset):
        """Hàm hỗ trợ load ảnh nút bấm với tọa độ X, Y tùy chỉnh"""
        path = os.path.join(PROJECT_ROOT, "Images", "Menu", filename)
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.smoothscale(img, (280, 140)) # Resize
        else:
            img = pygame.Surface((280, 140))
            img.fill((200, 200, 200))
        
        # Tạo rect tại vị trí trung tâm + offset
        rect = img.get_rect(center=(cx + x_offset, cy + y_offset))
        return img, rect

    def show(self):
        if not self.is_active:
            self.is_active = True
            self.show_buttons = False
            self.start_time = pygame.time.get_ticks()
            if self.win_sound:
                self.win_sound.play()

    def update(self):
        if not self.is_active: return

        if not self.show_buttons:
            elapsed = pygame.time.get_ticks() - self.start_time
            if elapsed > self.sound_duration:
                self.show_buttons = True

    def draw(self):
        if not self.is_active: return

        elapsed = pygame.time.get_ticks() - self.start_time
        scale = min(1.0, elapsed / 500) 
        scale = 1 + (2.70158 + 1) * pow(scale - 1, 3) + 2.70158 * pow(scale - 1, 2)
        if elapsed > 500: scale = 1.0

        orig_w, orig_h = self.congrats_img.get_size()
        new_w = int(orig_w * scale)
        new_h = int(orig_h * scale)
        scaled_img = pygame.transform.smoothscale(self.congrats_img, (new_w, new_h))
        
        # Đẩy ảnh Congratulation lên cao hơn một chút (-100px) để không che nút
        img_rect = scaled_img.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))

        if self.show_buttons:
            self.screen.blit(self.dim_surface, (0, 0))

        self.screen.blit(scaled_img, img_rect)

        if self.show_buttons:
            self.screen.blit(self.btn_restart_img, self.btn_restart_rect)
            self.screen.blit(self.btn_home_img, self.btn_home_rect)

    def handle_event(self, event):
        if not self.is_active or not self.show_buttons: return None

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_restart_rect.collidepoint(event.pos):
                return "restart"
            if self.btn_home_rect.collidepoint(event.pos):
                return "home"
        return None