import pygame
import json
import itertools  # <--- Thư viện mới để tạo tổ hợp
from gameplay.drag_item import DragItem
from gameplay.assemble_zone import AssembleZone
from quiz.quiz import QuizManager
from config import *

class Gameplay:
    def __init__(self, screen, robot_id, blueprint_bg):
        self.screen = screen
        self.robot_id = robot_id
        self.blueprint_bg = blueprint_bg
        self.robot_folder = robot_id
        self.robot_key = robot_id.lower()

        self.zone = AssembleZone()
        self.zone.set_state("body", robot_id)

        self.parts = [
            DragItem("head",  (300, 520), self.robot_folder),
            DragItem("track", (450, 520), self.robot_folder),
            DragItem("arm",   (600, 520), self.robot_folder),
            DragItem("power", (750, 520), self.robot_folder),
        ]

        # ====================================================
        # ⭐ TỰ ĐỘNG TẠO LOGIC LẮP RÁP (CHO 16 ẢNH)
        # ====================================================
        self.assembly_logic = {}
        
        # Danh sách các bộ phận (tên phải khớp với DragItem)
        opt_parts = ["arm", "head", "power", "track"]

        # Hàm tạo tên file ảnh theo quy tắc sắp xếp A-Z
        def make_state_name(part_list):
            if len(part_list) == 4:
                return f"{self.robot_key}_full_body" # Tên đặc biệt cho full
            if not part_list:
                return "body"
            # Sắp xếp a-z để đảm bảo body_arm_head giống body_head_arm
            return "body_" + "_".join(sorted(part_list))

        # Vòng lặp tạo ra tất cả các trường hợp có thể xảy ra
        # Duyệt qua số lượng bộ phận từ 0 đến 4
        for i in range(5): 
            # Lấy tất cả các tổ hợp (combinations) có i bộ phận
            for current_combo in itertools.combinations(opt_parts, i):
                current_state = make_state_name(current_combo)
                
                # Với trạng thái hiện tại, thử lắp thêm 1 món chưa có
                for part in opt_parts:
                    if part not in current_combo:
                        # Trạng thái mới = Danh sách cũ + Món mới
                        new_combo = list(current_combo) + [part]
                        next_state = make_state_name(new_combo)
                        
                        # Thêm vào từ điển logic: (Trạng thái cũ, Món thêm vào) -> Trạng thái mới
                        self.assembly_logic[(current_state, part)] = next_state
        
        # In ra để kiểm tra (bạn có thể xóa dòng này sau)
        # print(f"Đã tạo {len(self.assembly_logic)} quy tắc lắp ráp!")
        # ====================================================

        self.quiz = QuizManager(SCREEN_WIDTH, SCREEN_HEIGHT)

        # FIX JSON (Giữ nguyên phần fix lỗi trước đó)
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
        if self.quiz.is_active:
            self.quiz.handle_input(event)
            return

        for part in self.parts:
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
        result = self.quiz.update()
        
        if result is not None and self.pending_part:
            if result:
                self._try_assemble()
            else:
                self.pending_part.reset()
                self.zone.wrong_animation()
            
            self.pending_part = None

    def _try_assemble(self):
        current_state = self.zone.current_state
        part_name = self.pending_part.name
        
        # Tra từ điển (đã được tạo tự động ở trên)
        next_state = self.assembly_logic.get((current_state, part_name))
        
        if next_state:
            self.zone.set_state(next_state, self.robot_id)
            self.parts.remove(self.pending_part)
        else:
            # Trường hợp này hiếm khi xảy ra nếu bạn vẽ đủ 16 ảnh
            print(f"⚠️ Không tìm thấy ảnh cho: {current_state} + {part_name}")
            self.pending_part.reset()
            self.zone.wrong_animation()

    def draw(self):
        self.blueprint_bg.draw(self.screen)
        self.zone.draw(self.screen)
        for part in self.parts:
            part.draw(self.screen)
        self.quiz.draw(self.screen)