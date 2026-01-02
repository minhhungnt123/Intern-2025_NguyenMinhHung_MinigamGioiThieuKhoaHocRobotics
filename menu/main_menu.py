import pygame
import os
from config import *

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()

        # --- 1. LOAD ASSETS MENU CHÍNH ---
        # Ảnh nền text
        self.menu_text_size = (750, 400)
        path_bg = os.path.join(PROJECT_ROOT, "Images", "Menu", "menu_text.png")
        if os.path.exists(path_bg):
            self.bg_image = pygame.image.load(path_bg).convert_alpha()
            self.bg_image = pygame.transform.smoothscale(self.bg_image, self.menu_text_size)
        else:
            self.bg_image = pygame.Surface(self.menu_text_size); self.bg_image.fill((255, 200, 100))

        # Nút Start & Setting
        self.btn_size = (350, 150)
        self.btn_start_img, self.btn_start_rect = self._load_img("start_button.png", 0, 100, self.btn_size)
        self.btn_setting_img, self.btn_setting_rect = self._load_img("setting_button.png", 0, 230, self.btn_size)

        # --- 2. LOAD ASSETS CHO SETTING POPUP ---
        self.show_settings = False
        
        # Font chữ
        try:
            self.font = pygame.font.Font(os.path.join(PROJECT_ROOT, "Fonts", "Montserrat-Bold.ttf"), 32)
        except:
            self.font = pygame.font.SysFont("Arial", 32, bold=True)

        # Load ảnh Sound/Mute
        self.icon_on = self._load_icon("sound.png")
        self.icon_off = self._load_icon("mute.png")

        # Vị trí các nút Sound/Music/Close
        cx, cy = self.width // 2, self.height // 2
        self.bgm_rect = pygame.Rect(0, 0, 100, 60); self.bgm_rect.center = (cx + 40, cy - 30)
        self.sfx_rect = pygame.Rect(0, 0, 100, 60); self.sfx_rect.center = (cx + 40, cy + 50)
        self.btn_close_img, self.btn_close_rect = self._load_img("close_button.png", 0, 130, (140, 70))

        # Màn đen mờ che phía sau
        self.dim_surface = pygame.Surface((self.width, self.height))
        self.dim_surface.set_alpha(200)
        self.dim_surface.fill((0, 0, 0))

        # Animation state
        self.state = "INTRO"
        self.alpha = 0
        self.fade_speed = 6

    def _load_img(self, name, x_off, y_off, size):
        """Hàm hỗ trợ load ảnh và tạo rect tại vị trí mong muốn"""
        path = os.path.join(PROJECT_ROOT, "Images", "Menu", name)
        cx, cy = self.width // 2, self.height // 2
        
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.smoothscale(img, size)
        else:
            img = pygame.Surface(size)
            img.fill((200, 50, 50))
        
        rect = img.get_rect(center=(cx + x_off, cy + y_off))
        return img, rect

    def _load_icon(self, name):
        path = os.path.join(PROJECT_ROOT, "Images", "Menu", name)
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.smoothscale(img, (140, 70))
        return pygame.Surface((140, 70))

    def update(self):
        # Animation Fade In/Out
        if self.state == "INTRO":
            self.alpha += self.fade_speed
            if self.alpha >= 255: self.alpha = 255; self.state = "ACTIVE"
        elif self.state == "OUTRO":
            self.alpha -= self.fade_speed
            if self.alpha <= 0: self.alpha = 0; return "START_GAME"
        return None

    def handle_event(self, event):
        # 1. XỬ LÝ KHI ĐANG MỞ SETTING
        if self.show_settings:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                
                # Nút Close (Kiểm tra va chạm với Rect của ảnh)
                if self.btn_close_rect.collidepoint(event.pos):
                    self.show_settings = False
                    return None

                # Toggle BGM
                if self.bgm_rect.collidepoint(event.pos):
                    SOUND_SETTINGS["bgm_on"] = not SOUND_SETTINGS["bgm_on"]
                    return "toggle_bgm"
                
                # Toggle SFX
                if self.sfx_rect.collidepoint(event.pos):
                    SOUND_SETTINGS["sfx_on"] = not SOUND_SETTINGS["sfx_on"]
                    return "toggle_sfx"
            return None

        # 2. XỬ LÝ MENU CHÍNH (Khi không mở setting)
        if self.state != "ACTIVE": return None

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_start_rect.collidepoint(event.pos):
                self.state = "OUTRO"
            elif self.btn_setting_rect.collidepoint(event.pos):
                self.show_settings = True
        return None

    def draw(self):
        # Vẽ nền và nút menu chính
        self.bg_image.set_alpha(self.alpha)
        self.btn_start_img.set_alpha(self.alpha)
        self.btn_setting_img.set_alpha(self.alpha)

        cx, cy = self.width // 2, self.height // 2
        bg_rect = self.bg_image.get_rect(center=(cx, cy - 120))
        
        self.screen.blit(self.bg_image, bg_rect)
        self.screen.blit(self.btn_start_img, self.btn_start_rect)
        self.screen.blit(self.btn_setting_img, self.btn_setting_rect)

        # --- VẼ BẢNG SETTING (POPUP) ---
        if self.show_settings:
            # 1. Màn đen mờ
            self.screen.blit(self.dim_surface, (0, 0))

            # 2. Khung bảng
            panel_rect = pygame.Rect(0, 0, 400, 320)
            panel_rect.center = (cx, cy)
            pygame.draw.rect(self.screen, (50, 50, 70), panel_rect, border_radius=20)
            pygame.draw.rect(self.screen, (255, 255, 255), panel_rect, 3, border_radius=20)

            # 3. Tiêu đề
            title = self.font.render("SETTINGS", True, (255, 215, 0))
            self.screen.blit(title, title.get_rect(center=(cx, cy - 100)))

            # 4. Dòng 1: MUSIC (BGM)
            txt_bgm = self.font.render("BGM", True, (255, 255, 255))
            self.screen.blit(txt_bgm, (cx - 150, cy - 45))
            icon_bgm = self.icon_on if SOUND_SETTINGS["bgm_on"] else self.icon_off
            self.screen.blit(icon_bgm, self.bgm_rect)

            # 5. Dòng 2: SOUND (SFX)
            txt_sfx = self.font.render("SFX", True, (255, 255, 255))
            self.screen.blit(txt_sfx, (cx - 150, cy + 35))
            icon_sfx = self.icon_on if SOUND_SETTINGS["sfx_on"] else self.icon_off
            self.screen.blit(icon_sfx, self.sfx_rect)

            # 6. Nút Close (Vẽ ảnh thay vì Button class)
            self.screen.blit(self.btn_close_img, self.btn_close_rect)