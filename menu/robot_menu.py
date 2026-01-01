import pygame
import os
from config import *

class RobotSelectMenu:
    def __init__(self, screen):
        self.screen = screen
        self.selected_robot = None
        
        # --- 1. NÚT BACK (ICON HOME) ---
        self.home_btn_img = None
        self.home_btn_rect = None
        
        home_path = os.path.join(PROJECT_ROOT, "Images", "Menu", "home.png")
        if os.path.exists(home_path):
            img = pygame.image.load(home_path).convert_alpha()
            self.home_btn_img = pygame.transform.smoothscale(img, (140, 70)) # Resize icon nhỏ lại
            self.home_btn_rect = self.home_btn_img.get_rect(topleft=(140, 70))
        else:
            # Fallback nếu thiếu ảnh
            self.home_btn_img = pygame.Surface((140, 70))
            self.home_btn_img.fill((200, 50, 50))
            self.home_btn_rect = self.home_btn_img.get_rect(topleft=(140, 70))

        # --- 2. CẤU HÌNH FONT ---
        try:
            self.label_font = pygame.font.Font(os.path.join(PROJECT_ROOT, "Fonts", "Montserrat-Bold.ttf"), 28)
        except:
            self.label_font = pygame.font.SysFont("Arial", 28, bold=True)

        # --- 3. DATA LEVELS ---
        # Lưu ý: Robot 2 và 3 đang dùng tạm ảnh Robot 1 vì bạn chưa upload ảnh full_body của chúng
        self.levels = [
            {
                "id": "robot_1", 
                "level_img": "level1.png", 
                "robot_img": "robot_1_full_body.png", 
            },
            {
                "id": "robot_2", 
                "level_img": "level2.png", 
                "robot_img": "robot_2_full_body.png", 
            },
            {
                "id": "robot_3", 
                "level_img": "level3.png", 
                "robot_img": "robot_3_full_body.png", 
            },
        ]

        # Kích thước thẻ bài
        self.card_w, self.card_h = 240, 320
        gap = 50
        
        # Tính vị trí để căn giữa 3 thẻ
        total_w = (self.card_w * 3) + (gap * 2)
        start_x = (SCREEN_WIDTH - total_w) // 2
        start_y = (SCREEN_HEIGHT - self.card_h) // 2 + 40

        self.cards = []

        # --- 4. LOAD ẢNH VÀ TẠO RECT ---
        for i, item in enumerate(self.levels):
            # A. Load ảnh Level (Badge)
            lvl_path = os.path.join(PROJECT_ROOT, "Images", "Menu", item["level_img"])
            if os.path.exists(lvl_path):
                l_img = pygame.image.load(lvl_path).convert_alpha()
                item["lvl_surf"] = pygame.transform.smoothscale(l_img, (180, 100)) # Badge kích thước 180x100
            else:
                item["lvl_surf"] = pygame.Surface((180, 100))
                item["lvl_surf"].fill((255, 215, 0))

            # B. Load ảnh Robot (Preview)
            # Ưu tiên lấy trong thư mục Menu trước (như file bạn upload)
            robo_path = os.path.join(PROJECT_ROOT, "Images", "Menu", item["robot_img"])
            if not os.path.exists(robo_path):
                robo_path = os.path.join(PROJECT_ROOT, "Images", "Robot_1", "robot_1_full_body.png")

            if os.path.exists(robo_path):
                r_img = pygame.image.load(robo_path).convert_alpha()
                # Scale robot sao cho vừa khít chiều ngang thẻ (trừ lề)
                scale_ratio = 180 / r_img.get_width() 
                new_h = int(r_img.get_height() * scale_ratio)
                item["robo_surf"] = pygame.transform.smoothscale(r_img, (180, new_h))
            else:
                item["robo_surf"] = pygame.Surface((180, 200))
                item["robo_surf"].fill((100, 100, 100))

            # C. Tạo Rect cho thẻ
            x = start_x + i * (self.card_w + gap)
            rect = pygame.Rect(x, start_y, self.card_w, self.card_h)
            self.cards.append(rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()

            # 1. Check nút Home (Back)
            if self.home_btn_rect.collidepoint(mouse_pos):
                print("Back to Main Menu")
                return "back" # Trả về tín hiệu để Main Menu xử lý

            # 2. Check chọn Robot
            for i, card_rect in enumerate(self.cards):
                if card_rect.collidepoint(mouse_pos):
                    self.selected_robot = self.levels[i]["id"]
                    print(f"Selected: {self.levels[i]['id']}")

    def draw(self):
        # Vẽ nút Back (Home Icon)
        self.screen.blit(self.home_btn_img, self.home_btn_rect)
        
        mouse_pos = pygame.mouse.get_pos()

        for i, card_rect in enumerate(self.cards):
            data = self.levels[i]
            
            # --- HIỆU ỨNG HOVER ---
            is_hover = card_rect.collidepoint(mouse_pos)
            
            # Nếu hover thì thẻ nổi lên một chút (dịch y lên 10px)
            draw_y = card_rect.y - 10 if is_hover else card_rect.y
            
            # Màu nền thẻ
            bg_color = (40, 44, 52) if not is_hover else (50, 55, 65)
            border_color = (80, 80, 80) if not is_hover else (100, 200, 255)
            
            # Rect vẽ thực tế (có tính hover)
            draw_rect = pygame.Rect(card_rect.x, draw_y, card_rect.width, card_rect.height)

            # 1. Vẽ nền thẻ
            pygame.draw.rect(self.screen, bg_color, draw_rect, border_radius=20)
            pygame.draw.rect(self.screen, border_color, draw_rect, width=3, border_radius=20)

            # 2. Vẽ hình Robot (Canh giữa thẻ)
            r_surf = data["robo_surf"]
            r_rect = r_surf.get_rect(center=draw_rect.center)
            r_rect.y += 20 # Dịch xuống chút để nhường chỗ cho Badge Level
            self.screen.blit(r_surf, r_rect)

            # 3. Vẽ Badge Level (Nổi lên trên mép thẻ)
            # Vị trí: Giữa chiều ngang, mép trên đè lên đường viền
            l_surf = data["lvl_surf"]
            l_rect = l_surf.get_rect(center=(draw_rect.centerx, draw_rect.top)) 
            self.screen.blit(l_surf, l_rect)

    def get_selected_robot(self):
        return self.selected_robot
    
    def update(self):
        pass