import pygame
import json
import os
from config import *

from gameplay.drag_item import DragItem
from gameplay.assemble_zone import AssembleZone
from gameplay.camera import CameraZoom
from quiz.quiz import QuizManager

# Import Class Robot1
from robots.robot_1 import Robot1

class Gameplay:
    def __init__(self, screen, robot_id, blueprint_bg):
        self.screen = screen
        self.robot_id = robot_id
        self.blueprint_bg = blueprint_bg

        # ===== LOAD ROBOT DATA =====
        # Chọn class robot dựa trên ID (sau này có Robot2 thì thêm vào dict này)
        ROBOT_MAP = {
            "Robot_1": Robot1
        }
        
        # Lấy class config tương ứng, nếu không thấy thì mặc định Robot1
        RobotClass = ROBOT_MAP.get(robot_id, Robot1)
        self.robot_config = RobotClass() # Khởi tạo

        # ===== CAMERA =====
        self.camera = CameraZoom()

        # ===== ASSEMBLE ZONE (Vùng lắp ráp) =====
        self.zone = AssembleZone()
        # Set trạng thái ban đầu từ config (ví dụ: "body")
        self.zone.set_state(self.robot_config.INITIAL_STATE, robot_id)

        # ===== DRAG PARTS (Các bộ phận rời) =====
        self.parts = []
        # Tạo danh sách part từ config PARTS_LIST
        for p in self.robot_config.PARTS_LIST:
            # p["name"] là 'head', p["pos"] là (300, 600)...
            item = DragItem(p["name"], p["pos"], robot_id)
            self.parts.append(item)

        # ===== HÌNH MẪU (FULL BODY) =====
        self.full_body_img = None
        full_body_path = os.path.join(PROJECT_ROOT, "Images", robot_id, self.robot_config.FULL_BODY_IMAGE)
        if os.path.exists(full_body_path):
            img = pygame.image.load(full_body_path).convert_alpha()
            self.full_body_img = pygame.transform.smoothscale(img, (150, 150))

        # ===== QUIZ =====
        self.quiz = QuizManager(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Load câu hỏi
        quiz_path = os.path.join(PROJECT_ROOT, "quiz", "questions.json")
        with open(quiz_path, encoding="utf-8") as f:
            data = json.load(f)
            self.questions = data.get(robot_id, [])

        self.pending_part = None

    # ==================================================
    def handle_event(self, event):
        if self.quiz.is_active:
            self.quiz.handle_event(event)
            return

        for part in self.parts:
            part.handle_event(event)

        # Xử lý khi thả chuột (Mouse Up)
        if event.type == pygame.MOUSEBUTTONUP:
            for part in self.parts:
                # Nếu part được thả vào vùng Zone
                if part.rect.colliderect(self.zone.rect):
                    self.pending_part = part
                    
                    # Lấy câu hỏi tiếp theo
                    if self.questions:
                        question = self.questions.pop(0)
                        # Trả part bộ phận về chỗ cũ trước khi hiện quiz để không bị che
                        part.reset()
                        self.quiz.start_quiz(question)
                    else:
                        print("Hết câu hỏi!")
                    break

    # ==================================================
    def update(self):
        self.camera.update()
        if not self.blueprint_bg.done:
            self.blueprint_bg.update()

        # Update Quiz và nhận kết quả
        result = self.quiz.update()
        
        # Nếu có kết quả trả về (True/False) và đang có bộ phận chờ lắp
        if result is not None and self.pending_part:
            if result == True:
                # === TRẢ LỜI ĐÚNG ===
                print("Đúng! Đang kiểm tra logic lắp ráp...")
                
                # 1. Lấy trạng thái hiện tại (vd: "body")
                current_state = self.zone.current_state
                # 2. Lấy tên bộ phận đang lắp (vd: "head")
                part_name = self.pending_part.name
                
                # 3. Tra bảng logic trong robot_1.py
                # logic_map = {"head": "head_body", ...}
                logic_map = self.robot_config.ASSEMBLY_LOGIC.get(current_state, {})
                
                if part_name in logic_map:
                    # Hợp lệ -> Lấy trạng thái mới (vd: "head_body")
                    new_state = logic_map[part_name]
                    self.zone.set_state(new_state, self.robot_id)
                    
                    # Xóa bộ phận đó khỏi danh sách (vì đã lắp rồi)
                    if self.pending_part in self.parts:
                        self.parts.remove(self.pending_part)
                else:
                    # Trả lời đúng nhưng lắp sai thứ tự (vd: chưa có tay mà lắp súng)
                    print("Lắp sai thứ tự!")
                    self.zone.wrong_animation()
                    
            else:
                # === TRẢ LỜI SAI ===
                print("Sai rồi!")
                self.zone.wrong_animation()

            # Reset biến chờ
            self.pending_part = None

    # ==================================================
    def draw_game_objects(self, surface):
        # 1. Vẽ nền
        self.blueprint_bg.draw(surface)

        # 2. Vẽ Robot đang lắp (Zone)
        self.zone.draw(surface)

        # 3. Vẽ các bộ phận rời
        for part in self.parts:
            part.draw(surface)
            
        # 4. Vẽ hình mẫu (Góc trái trên)
        if self.full_body_img:
            # Vẽ khung trắng bao quanh
            pygame.draw.rect(surface, (255, 255, 255), (15, 15, 160, 160), 3, border_radius=10)
            surface.blit(self.full_body_img, (20, 20))

        # 5. Vẽ Quiz (Trên cùng)
        self.quiz.draw(surface)

    # ==================================================
    def draw(self):
        temp = pygame.Surface(self.screen.get_size())
        self.draw_game_objects(temp)
        zoomed = self.camera.apply(temp)
        self.screen.blit(zoomed, (0, 0))