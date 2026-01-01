import pygame
import os
from config import *

class FinishMenu:
    def __init__(self, screen):
        self.screen = screen
        self.is_active = False
        
        # --- TRẠNG THÁI ANIMATION ---
        # 0: Mới hiện (đứng im giữa màn hình)
        # 1: Đang trượt sang trái
        # 2: Đã trượt xong & Hiện menu nút
        self.anim_phase = 0
        self.slide_speed = 15  # Tốc độ trượt
        
        # --- LOAD HÌNH ẢNH ---
        self._load_assets()

        # --- CẤU HÌNH VỊ TRÍ ---
        # Vị trí ban đầu (Giữa màn hình)
        self.center_x = SCREEN_WIDTH // 2
        self.center_y = SCREEN_HEIGHT // 2
        
        # Vị trí đích sau khi trượt (Lệch sang trái)
        self.target_x = 350 
        
        # Rect của hình chúc mừng
        self.congrat_rect = self.congrat_img.get_rect(center=(self.center_x, self.center_y))

        # --- DANH SÁCH NÚT ---
        # Gồm: Level 1, Level 2, Level 3, Restart, Home
        # Level buttons sẽ tượng trưng cho Robot 1, 2, 3
        self.buttons = []
        self._init_buttons()

    def _load_assets(self):
        # 1. Hình nền mờ
        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.overlay.set_alpha(180) # Độ mờ
        self.overlay.fill((0, 0, 0))

        # 2. Hình Congratulation
        path = os.path.join(PROJECT_ROOT, "Images", "Menu", "congratulation.png")
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            # Scale to khoảng 60% màn hình để còn chỗ cho nút
            self.congrat_img = pygame.transform.smoothscale(img, (600, 450)) 
        else:
            self.congrat_img = pygame.Surface((600, 450))
            self.congrat_img.fill((255, 215, 0))

    def _init_buttons(self):
        # Khu vực bên phải để đặt nút (từ x=700 trở đi)
        start_x = 850
        start_y = 200
        gap_y = 100 # Khoảng cách giữa các nút

        # Helper load ảnh nút
        def make_btn(name, x, y, tag, scale=(180, 70)):
            path = os.path.join(PROJECT_ROOT, "Images", "Menu", name)
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.smoothscale(img, scale)
            else:
                img = pygame.Surface(scale)
                img.fill((200, 200, 200))
            
            rect = img.get_rect(center=(x, y))
            return {"image": img, "rect": rect, "tag": tag}

        # Tạo 3 nút Level (Tương ứng Robot 1, 2, 3)
        self.buttons = [
            make_btn("level1.png", start_x, start_y, "robot_1"),
            make_btn("level2.png", start_x, start_y + gap_y, "robot_2"),
            make_btn("level3.png", start_x, start_y + gap_y * 2, "robot_3"),
        ]

        # Tạo 2 nút chức năng nhỏ hơn ở dưới cùng (Restart, Home)
        btn_func_y = start_y + gap_y * 3 + 20
        self.buttons.append(make_btn("restart_button.png", start_x - 80, btn_func_y, "restart", (180, 70)))
        self.buttons.append(make_btn("home.png", start_x + 80, btn_func_y, "home", (180, 70)))

    def show(self):
        self.is_active = True
        self.anim_phase = 0
        # Reset vị trí về giữa
        self.congrat_rect.center = (self.center_x, self.center_y)
        
        # Play sound victory nếu có
        win_sound = os.path.join(PROJECT_ROOT, "Sound", "winning.mp3")
        if os.path.exists(win_sound) and SOUND_SETTINGS["sfx_on"]:
            pygame.mixer.Sound(win_sound).play()

    def update(self):
        if not self.is_active: return

        # LOGIC ANIMATION
        if self.anim_phase == 0:
            # Chờ 1 chút (khoảng 60 frame ~ 1 giây) rồi mới trượt
            # Ở đây mình làm đơn giản: cho trượt luôn hoặc chờ user click
            # Để tự động trượt:
            self.anim_phase = 1

        elif self.anim_phase == 1:
            # Di chuyển sang trái
            if self.congrat_rect.centerx > self.target_x:
                self.congrat_rect.centerx -= self.slide_speed
            else:
                # Đã đến đích -> Hiện nút
                self.congrat_rect.centerx = self.target_x
                self.anim_phase = 2

    def handle_event(self, event):
        if not self.is_active: return None
        
        # Chỉ xử lý click khi animation đã xong (Phase 2)
        if self.anim_phase == 2:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for btn in self.buttons:
                        if btn["rect"].collidepoint(event.pos):
                            return btn["tag"] # Trả về: "robot_1", "restart", "home"...
        return None

    def draw(self):
        if not self.is_active: return

        # 1. Vẽ nền tối
        self.screen.blit(self.overlay, (0, 0))

        # 2. Vẽ hình Congratulation (Vị trí cập nhật theo update)
        self.screen.blit(self.congrat_img, self.congrat_rect)

        # 3. Vẽ các nút (Chỉ vẽ khi Phase == 2)
        if self.anim_phase == 2:
            for btn in self.buttons:
                self.screen.blit(btn["image"], btn["rect"])