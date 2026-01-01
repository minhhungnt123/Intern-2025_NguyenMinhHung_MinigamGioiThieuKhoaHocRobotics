import pygame
import json
import itertools
from gameplay.drag_item import DragItem
from gameplay.assemble_zone import AssembleZone
from quiz.quiz import QuizManager
from config import *

# --- IMPORT MENU MỚI ---
from menu.finish_menu import FinishMenu 

class Gameplay:
    def __init__(self, screen, robot_id, blueprint_bg):
        self.screen = screen
        self.robot_id = robot_id
        self.blueprint_bg = blueprint_bg
        self.robot_key = robot_id.lower()
        self.finish_menu = FinishMenu(screen) # Giữ nguyên code menu của bạn

        # ====================================================
        # ⭐ 1. CẤU HÌNH CÁC BỘ PHẬN CHO TỪNG ROBOT
        # ====================================================
        # Định nghĩa xem mỗi robot có những bộ phận rời nào
        ROBOT_CONFIGS = {
            "robot_1": ["head", "track"],                   # Level 1: 2 món (+ body = 3)
            "robot_2": ["head", "law", "engine"],            # Level 2: 3 món (+ body = 4)
            "robot_3": ["head", "track", "arm", "power"],   # Level 3: 4 món (+ body = 5)
        }
        
        # Lấy danh sách bộ phận dựa trên ID, mặc định là full nếu không tìm thấy
        opt_parts = ROBOT_CONFIGS.get(self.robot_key, ["head", "track", "arm", "power"])
        
        # ====================================================
        # ⭐ 2. TẠO DRAG ITEM TỰ ĐỘNG DỰA TRÊN DANH SÁCH
        # ====================================================
        self.parts = []
        
        # Định nghĩa vị trí cố định trên bàn cho từng loại bộ phận (để nó không chồng lên nhau)
        # Bạn có thể chỉnh lại toạ độ x, y cho đẹp
        POSITIONS = {
            "head":  (300, 520),
            "track": (450, 520),
            "arm":   (600, 520),
            "power": (750, 520)
        }

        for part_name in opt_parts:
            # Lấy vị trí từ điển, nếu không có thì để mặc định (0,0)
            pos = POSITIONS.get(part_name, (100, 100)) 
            self.parts.append(DragItem(part_name, pos, self.robot_id))

        self.zone = AssembleZone()
        self.zone.set_state("body", robot_id)

        # ====================================================
        # ⭐ 3. LOGIC LẮP RÁP (TỰ ĐỘNG SINH RA THEO SỐ LƯỢNG BỘ PHẬN)
        # ====================================================
        self.assembly_logic = {}
        
        def make_state_name(part_list):
            # Nếu số lượng bộ phận đã lắp = tổng số bộ phận cần thiết
            if len(part_list) == len(opt_parts):
                return f"{self.robot_key}_full_body"
            if not part_list:
                return "body"
            return "body_" + "_".join(sorted(part_list))

        # Vòng lặp này tự động chạy đúng bất kể có bao nhiêu bộ phận (2, 3 hay 4)
        for i in range(len(opt_parts) + 1): 
            for current_combo in itertools.combinations(opt_parts, i):
                current_state = make_state_name(current_combo)
                for part in opt_parts:
                    if part not in current_combo:
                        new_combo = list(current_combo) + [part]
                        next_state = make_state_name(new_combo)
                        self.assembly_logic[(current_state, part)] = next_state

        self.quiz = QuizManager(SCREEN_WIDTH, SCREEN_HEIGHT)

        # Load câu hỏi
        with open("quiz/questions.json", encoding="utf-8") as f:
            raw_data = json.load(f)[self.robot_key]
        self.questions = []
        for q in raw_data:
            formatted_q = {
                "question": q["question"],
                "options": q["options"],
                "correct_index": q["answer"]
            }
            self.questions.append(formatted_q)

        self.pending_part = None

    def handle_event(self, event):
        # 1. Nếu đã thắng -> Chuyển sự kiện cho FinishMenu xử lý
        if self.finish_menu.is_active:
            return self.finish_menu.handle_event(event)

        # 2. Logic game bình thường
        if self.quiz.is_active:
            self.quiz.handle_input(event)
            return

        for part in reversed(self.parts):
            part.handle_event(event)

        if event.type == pygame.MOUSEBUTTONUP:
            for part in self.parts:
                if part.rect.colliderect(self.zone.rect):
                    self.pending_part = part
                    if len(self.questions) > 0:
                        question = self.questions.pop(0)
                        self.quiz.start_quiz(question)
                    else:
                        self._try_assemble()
                    break

    def update(self):
        # 1. Update Finish Menu
        if self.finish_menu.is_active:
            self.finish_menu.update()
            return

        # 2. Update Game logic
        result = self.quiz.update()
        if result is not None and self.pending_part:
            if result:
                self._try_assemble()
            else:
                self.pending_part.reset()
                self.zone.wrong_animation()
            self.pending_part = None
        
        # 3. KIỂM TRA ĐIỀU KIỆN THẮNG
        # Nếu hết linh kiện và không còn đang giữ linh kiện nào
        if not self.parts and not self.pending_part and not self.quiz.is_active:
            self.finish_menu.show() # Kích hoạt menu chiến thắng

    def _try_assemble(self):
        current_state = self.zone.current_state
        part_name = self.pending_part.name
        next_state = self.assembly_logic.get((current_state, part_name))
        
        if next_state:
            self.zone.set_state(next_state, self.robot_id)
            self.parts.remove(self.pending_part)
        else:
            self.pending_part.reset()
            self.zone.wrong_animation()

    def draw(self):
        # Vẽ nền và game
        self.blueprint_bg.draw(self.screen)
        self.zone.draw(self.screen)
        for part in self.parts:
            part.draw(self.screen)
        self.quiz.draw(self.screen)

        # Vẽ Menu chiến thắng đè lên trên cùng (nếu active)
        self.finish_menu.draw()