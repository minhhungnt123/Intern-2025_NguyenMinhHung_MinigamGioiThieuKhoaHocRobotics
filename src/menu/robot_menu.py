import pygame
import os
from config import *

# --- CLASS HỖ TRỢ ANIMATION ---
class SpriteAnimation:
    # ⭐ Thêm tham số n_frames vào đây
    def __init__(self, image_path, scale_size, n_frames=1):
        self.frames = []
        self.current_frame = 0
        self.last_update = 0
        self.cooldown = 100 

        if os.path.exists(image_path):
            sprite_sheet = pygame.image.load(image_path).convert_alpha()
            sheet_w, sheet_h = sprite_sheet.get_size()
            
            if n_frames > 0:
                frame_width = sheet_w // n_frames
                
                for i in range(n_frames):
                    frame = sprite_sheet.subsurface((i * frame_width, 0, frame_width, sheet_h))
                    scaled = pygame.transform.smoothscale(frame, scale_size)
                    self.frames.append(scaled)
        
        if not self.frames:
            s = pygame.Surface(scale_size); s.fill((100, 100, 100))
            self.frames.append(s)

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.cooldown:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.frames)

    def get_image(self):
        return self.frames[self.current_frame]

# --- MENU CHÍNH ---
class RobotSelectMenu:
    def __init__(self, screen):
        self.screen = screen
        self.selected_robot = None
        
        # Nút Back
        self.home_btn_img = None
        self.home_btn_rect = None
        home_path = os.path.join(PROJECT_ROOT, "Images", "Menu", "home.png")
        if os.path.exists(home_path):
            img = pygame.image.load(home_path).convert_alpha()
            self.home_btn_img = pygame.transform.smoothscale(img, (150, 100))
        else:
            self.home_btn_img = pygame.Surface((150, 100)); self.home_btn_img.fill((200, 50, 50))
        self.home_btn_rect = self.home_btn_img.get_rect(topleft=(30, 30))

        try:
            self.label_font = pygame.font.Font(os.path.join(PROJECT_ROOT, "Font", "Montserrat-Bold.ttf"), 24)
        except:
            self.label_font = pygame.font.SysFont("Arial", 24, bold=True)
        self.levels = [
            {
                "id": "robot_1",
                "level_img": "level1.png",
                "idle_file": "robot_1_idle.png",
                "folder": "Robot_1",
                "label": "SCOUT",
                "frames": 12
            },
            {
                "id": "robot_2",
                "level_img": "level2.png",
                "idle_file": "robot_2_idle.png",
                "folder": "Robot_2",
                "label": "WELDER",
                "frames": 9
            },
            {
                "id": "robot_3",
                "level_img": "level3.png",
                "idle_file": "robot_3_Idle.png",
                "folder": "Robot_3",
                "label": "PANACER",
                "frames": 6
            },
        ]

        self.card_w, self.card_h = 240, 320
        gap = 50
        total_w = (self.card_w * 3) + (gap * 2)
        start_x = (SCREEN_WIDTH - total_w) // 2
        start_y = (SCREEN_HEIGHT - self.card_h) // 2 + 40

        self.cards = []

        # KHỞI TẠO CÁC CARD VÀ ANIMATION
        for i, item in enumerate(self.levels):
            # 1. Badge Level
            lvl_path = os.path.join(PROJECT_ROOT, "Images", "Menu", item["level_img"])
            if os.path.exists(lvl_path):
                l_img = pygame.image.load(lvl_path).convert_alpha()
                item["lvl_surf"] = pygame.transform.smoothscale(l_img, (150, 90))
            else:
                item["lvl_surf"] = pygame.Surface((150, 90)); item["lvl_surf"].fill((255, 215, 0))

            # 2. TẠO ANIMATION IDLE 
            idle_path = os.path.join(PROJECT_ROOT, "Images", item["folder"], item["idle_file"])
            custom_size = item.get("scale", (180, 180))
            frame_count = item.get("frames", 1)
            
            # Truyền số frame vào class
            item["anim"] = SpriteAnimation(idle_path, custom_size, frame_count)

            x = start_x + i * (self.card_w + gap)
            rect = pygame.Rect(x, start_y, self.card_w, self.card_h)
            self.cards.append(rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.home_btn_rect.collidepoint(event.pos):
                return "back"

            for i, card_rect in enumerate(self.cards):
                if card_rect.collidepoint(event.pos):
                    self.selected_robot = self.levels[i]["id"]

    def update(self):
        # ⭐ Cập nhật frame cho tất cả robot
        for item in self.levels:
            item["anim"].update()

    def draw(self):
        self.screen.blit(self.home_btn_img, self.home_btn_rect)
        mouse_pos = pygame.mouse.get_pos()

        for i, card_rect in enumerate(self.cards):
            data = self.levels[i]
            is_hover = card_rect.collidepoint(mouse_pos)
            
            draw_y = card_rect.y - 10 if is_hover else card_rect.y
            bg_color = (40, 44, 52) if not is_hover else (50, 55, 65)
            border_color = (80, 80, 80) if not is_hover else (100, 200, 255)
            
            draw_rect = pygame.Rect(card_rect.x, draw_y, card_rect.width, card_rect.height)

            pygame.draw.rect(self.screen, bg_color, draw_rect, border_radius=20)
            pygame.draw.rect(self.screen, border_color, draw_rect, width=3, border_radius=20)

            # VẼ ANIMATION FRAME
            r_surf = data["anim"].get_image()
            r_rect = r_surf.get_rect(center=draw_rect.center)
            r_rect.y += 15
            self.screen.blit(r_surf, r_rect)

            # Label
            name_surf = self.label_font.render(data["label"], True, (255, 255, 255))
            name_rect = name_surf.get_rect(center=(draw_rect.centerx, draw_rect.bottom - 30))
            self.screen.blit(name_surf, name_rect)

            # Badge Level
            l_surf = data["lvl_surf"]
            l_rect = l_surf.get_rect(center=(draw_rect.centerx, draw_rect.top)) 
            self.screen.blit(l_surf, l_rect)

    def get_selected_robot(self):
        return self.selected_robot