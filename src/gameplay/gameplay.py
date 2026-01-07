import pygame
import json
import itertools
import os
from gameplay.drag_item import DragItem
from gameplay.assemble_zone import AssembleZone
from quiz.quiz import QuizManager
from menu.finish_menu import FinishMenu
from config import *

# --- CLASS ANIMATION  ---
class SpriteAnimation:
    def __init__(self, image_path, scale_size, n_frames=1):
        self.frames = []
        self.current_frame = 0
        self.last_update = 0
        self.cooldown = 100 

        if os.path.exists(image_path):
            try:
                sprite_sheet = pygame.image.load(image_path).convert_alpha()
                sheet_w, sheet_h = sprite_sheet.get_size()
                if n_frames > 0:
                    frame_width = sheet_w // n_frames
                    for i in range(n_frames):
                        frame = sprite_sheet.subsurface((i * frame_width, 0, frame_width, sheet_h))
                        self.frames.append(pygame.transform.smoothscale(frame, scale_size))
            except Exception as e:
                print(f"⚠ Lỗi load animation {image_path}: {e}")
        
        if not self.frames:
            s = pygame.Surface(scale_size)
            s.fill((0, 255, 0))
            self.frames.append(s)

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.cooldown:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.frames)

    def get_image(self):
        return self.frames[self.current_frame]


class Gameplay:
    def __init__(self, screen, robot_id, blueprint_bg):
        self.screen = screen
        self.robot_id = robot_id
        self.blueprint_bg = blueprint_bg
        self.robot_key = robot_id.lower()
        
        self.finish_menu = FinishMenu(screen)
        self.zone = AssembleZone()
        self.zone.set_state("body", robot_id)

        self.is_paused = False

        # --- HELPER: ---
        def _load_image(path_parts, size=None):
            path = os.path.join(PROJECT_ROOT, *path_parts)
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                if size:
                    img = pygame.transform.smoothscale(img, size)
                return img
            # Trả về ô vuông màu nếu không tìm thấy ảnh
            fallback = pygame.Surface(size if size else (50, 50))
            fallback.fill((200, 200, 200))
            return fallback

        # 1. LOAD UI ASSETS (CARD & PAUSE)
        self.card_img = _load_image(["Images", "Menu", "card.png"])
        self.part_card_img = pygame.transform.smoothscale(self.card_img, (130, 130))
        self.preview_card_img = pygame.transform.smoothscale(self.card_img, (200, 200))

        # Nút Pause (Góc phải trên)
        self.pause_img = _load_image([PROJECT_ROOT, "Images", "Menu", "pause_button.png"], (100, 60))
        self.pause_rect = self.pause_img.get_rect(topright=(SCREEN_WIDTH - 20, 20))

        # 2. LOAD ROBOT PREVIEW (Góc trái trên)
        full_body_path = os.path.join(PROJECT_ROOT, "Images", self.robot_id, f"{self.robot_key}_full_body.png")
        if not os.path.exists(full_body_path): 
             full_body_path = os.path.join(PROJECT_ROOT, "Images", "Menu", f"{self.robot_key}_full_body.png")
        
        if os.path.exists(full_body_path):
            raw_prev = pygame.image.load(full_body_path).convert_alpha()
            scale_ratio = 160 / raw_prev.get_width()
            new_h = int(raw_prev.get_height() * scale_ratio)
            self.preview_img = pygame.transform.smoothscale(raw_prev, (160, new_h))
        else:
            self.preview_img = pygame.Surface((160, 160))
            self.preview_img.fill((100, 100, 100))

        # 3. PAUSE MENU (Popup)
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        
        self.btn_restart_img = _load_image([PROJECT_ROOT, "Images", "Menu", "restart_button.png"], (150, 80))
        self.btn_restart_rect = self.btn_restart_img.get_rect(center=(cx - 150, cy))
        
        self.btn_play_img = _load_image([PROJECT_ROOT, "Images", "Menu", "play_button.png"], (150, 80))
        self.btn_play_rect = self.btn_play_img.get_rect(center=(cx, cy))
        
        self.btn_home_img = _load_image([PROJECT_ROOT, "Images", "Menu", "home.png"], (150, 80))
        self.btn_home_rect = self.btn_home_img.get_rect(center=(cx + 150, cy))
        
        self.dim_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.dim_surface.set_alpha(150)
        self.dim_surface.fill((0, 0, 0))

        # [TỐI ƯU] Pre-render text PAUSED
        try:
            font_pause = pygame.font.SysFont("Arial", 50, bold=True)
            self.txt_pause = font_pause.render("PAUSED", True, (255, 255, 255))
        except:
            self.txt_pause = pygame.Surface((200, 50))
        self.txt_pause_rect = self.txt_pause.get_rect(center=(cx, cy - 120))

        # CẤU HÌNH BỘ PHẬN & LOGIC LẮP RÁP
        
        ROBOT_CONFIGS = {
            "robot_1": ["gun", "pinwheel"],                 
            "robot_2": ["engine", "head", "law"],           
            "robot_3": ["arm", "head", "power", "track"],   
        }
        
        RUN_FILES = {
            "robot_1": {"folder": "Robot_1", "file": "robot_1_run.png", "scale": (300, 300), "frames": 10},
            "robot_2": {"folder": "Robot_2", "file": "robot_2_run.png", "scale": (280, 320), "frames": 9},
            "robot_3": {"folder": "Robot_3", "file": "robot_3_run.png", "scale": (300, 300), "frames": 4},
        }
        ROBOT_SCALES = {
            "robot_1": 3.0,
            "robot_2": 2.5,
            "robot_3": 2.0
        }
        current_scale = ROBOT_SCALES.get(self.robot_key, 1.0)

        # 4. Tạo các bộ phận (DragItem)
        SIDEBAR_RIGHT_MARGIN = 180
        SIDEBAR_START_Y = 120        
        ITEM_SPACING_Y = 150         

        self.opt_parts = ROBOT_CONFIGS.get(self.robot_key, [])
        self.parts = []
        self.part_start_positions = [] 

        for index, part_name in enumerate(self.opt_parts):
            center_x = SCREEN_WIDTH - SIDEBAR_RIGHT_MARGIN
            center_y = SIDEBAR_START_Y + (index * ITEM_SPACING_Y)
            center_pos = (center_x, center_y)
            
            new_part = DragItem(part_name, center_pos, self.robot_id, scale_factor=current_scale)
            new_part.rect.center = center_pos
            if hasattr(new_part, 'start_pos'):
                new_part.start_pos = new_part.rect.topleft
            if hasattr(new_part, 'origin_pos'): 
                new_part.origin_pos = new_part.rect.topleft

            self.parts.append(new_part)
            self.part_start_positions.append(center_pos)

        # 5. Logic lắp ráp (Tự động sinh logic từ danh sách bộ phận)
        self.assembly_logic = {}
        def make_state_name(part_list):
            if len(part_list) == len(self.opt_parts): return f"{self.robot_key}_full_body"
            if not part_list: return "body"
            return "body_" + "_".join(sorted(part_list))

        for i in range(len(self.opt_parts) + 1): 
            for current_combo in itertools.combinations(self.opt_parts, i):
                current_state = make_state_name(current_combo)
                for part in self.opt_parts:
                    if part not in current_combo:
                        new_combo = list(current_combo) + [part]
                        self.assembly_logic[(current_state, part)] = make_state_name(new_combo)

        # 6. Khởi tạo Quiz
        self.quiz = QuizManager(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.questions = []
        try:
            json_path = os.path.join(PROJECT_ROOT, "quiz", "questions.json")
            with open(json_path, encoding="utf-8") as f:
                raw_data = json.load(f).get(self.robot_key, [])
        except Exception as e:
            print(f"Lỗi load quiz: {e}")
            raw_data = []
        
        for q in raw_data:
            self.questions.append({
                "question": q["question"],
                "options": q["options"],
                "correct_index": q["answer"]
            })
        
        self.backup_questions = list(self.questions)
        self.pending_part = None

        # 7. Animation Run (Victory)
        self.is_victory_run = False
        self.victory_start_time = 0
        self.run_duration = 5000 
        
        run_info = RUN_FILES.get(self.robot_key, {"folder": "Robot_1", "file": "robot_1_run.png", "frames": 1})
        run_path = os.path.join(PROJECT_ROOT, "Images", run_info.get("folder"), run_info.get("file"))
        self.run_anim = SpriteAnimation(run_path, run_info.get("scale", (300, 300)), run_info.get("frames", 1))
        
        self.run_pos_x = SCREEN_WIDTH // 2 - 150
        self.run_pos_y = SCREEN_HEIGHT // 2 - 150

    def handle_event(self, event):
        # Ưu tiên xử lý sự kiện Menu Kết Thúc
        if self.finish_menu.is_active:
            return self.finish_menu.handle_event(event)

        # Xử lý khi Pause
        if self.is_paused:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.btn_restart_rect.collidepoint(event.pos): return "restart"
                if self.btn_home_rect.collidepoint(event.pos): return "home"
                if self.btn_play_rect.collidepoint(event.pos): 
                    self.is_paused = False
            return None 

        # Không tương tác khi đang chạy chiến thắng
        if self.is_victory_run: return None

        # Nút Pause
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.pause_rect.collidepoint(event.pos):
                self.is_paused = True
                return None

        # Quiz input
        if self.quiz.is_active:
            self.quiz.handle_input(event)
            return

        # Drag & Drop Item
        for part in reversed(self.parts):
            if part.handle_event(event): break 

        if event.type == pygame.MOUSEBUTTONUP:
            for part in self.parts:
                if part.rect.colliderect(self.zone.rect):
                    self.pending_part = part
                    
                    # Nếu hết câu hỏi thì nạp lại từ backup
                    if len(self.questions) > 0:
                        self.quiz.start_quiz(self.questions[0])
                    # Có câu hỏi -> Hiện Quiz, Không -> Lắp luôn
                    if len(self.questions) > 0:
                        self.quiz.start_quiz(self.questions[0])
                    else:
                        self._try_assemble()
                    break

    def update(self):
        if self.finish_menu.is_active:
            self.finish_menu.update()
            return

        if self.is_paused:
            return 

        # Logic Victory Run
        if self.is_victory_run:
            self.run_anim.update()
            elapsed = pygame.time.get_ticks() - self.victory_start_time
            if elapsed >= self.run_duration:
                self.is_victory_run = False
                self.finish_menu.show()
            return

        # Logic Quiz result
        result = self.quiz.update()
        if result is not None and self.pending_part:
            if result: 
                # Đúng -> Lắp ráp
                self._try_assemble()
                if len(self.questions) > 0:
                    self.questions.pop(0)
            else:
                # Sai -> Reset vị trí, animation lắc đầu
                self.pending_part.reset()
                self.zone.wrong_animation()
                
                # Đẩy câu sai xuống cuối hàng đợi
                if len(self.questions) > 0:
                    current_q = self.questions.pop(0)
                    self.questions.append(current_q)
                    
            self.pending_part = None
        
        # Kiểm tra hoàn thành (hết part, không quiz, chưa run)
        if not self.parts and not self.pending_part and not self.quiz.is_active:
            if not self.is_victory_run and not self.finish_menu.is_active:
                print("🎉 Victory Run Start!")
                self.is_victory_run = True
                self.victory_start_time = pygame.time.get_ticks()

    def _try_assemble(self):
        current = self.zone.current_state
        part = self.pending_part.name
        nxt = self.assembly_logic.get((current, part))
        
        # Kiểm tra file ảnh tồn tại trước khi chuyển trạng thái
        if nxt and os.path.exists(os.path.join(PROJECT_ROOT, "Images", self.robot_id, f"{nxt}.png")):
            self.zone.set_state(nxt, self.robot_id)
            self.parts.remove(self.pending_part)
        else:
            self.pending_part.reset()
            self.zone.wrong_animation()

    def draw(self):
        # 1. Vẽ nền
        self.blueprint_bg.draw(self.screen)
        
        if self.is_victory_run:
            run_img = self.run_anim.get_image()
            self.screen.blit(run_img, (self.run_pos_x, self.run_pos_y))
        else:
            # 2. Vẽ vùng lắp ráp
            self.zone.draw(self.screen)

            # 3. Vẽ card nền cho các bộ phận
            for pos in self.part_start_positions:
                card_rect = self.part_card_img.get_rect(center=pos)
                self.screen.blit(self.part_card_img, card_rect)

            # 4. Vẽ các bộ phận
            for part in self.parts:
                part.draw(self.screen)
            
            # 5. Vẽ Preview Robot (Góc trái)
            preview_card_rect = self.preview_card_img.get_rect(topleft=(20, 20))
            self.screen.blit(self.preview_card_img, preview_card_rect)
            
            prev_rect = self.preview_img.get_rect(center=preview_card_rect.center)
            prev_rect.y -= 10 
            self.screen.blit(self.preview_img, prev_rect)

            # 6. UI: Nút Pause
            self.screen.blit(self.pause_img, self.pause_rect)
            
            # 7. Vẽ Quiz (Nếu đang active)
            self.quiz.draw(self.screen)

        # 8. Vẽ Overlay Menu Pause
        if self.is_paused:
            self.screen.blit(self.dim_surface, (0, 0))
            
            self.screen.blit(self.txt_pause, self.txt_pause_rect)
            self.screen.blit(self.btn_restart_img, self.btn_restart_rect)
            self.screen.blit(self.btn_play_img, self.btn_play_rect) 
            self.screen.blit(self.btn_home_img, self.btn_home_rect)

        # 9. Vẽ Menu Finish (Nếu active)
        self.finish_menu.draw()