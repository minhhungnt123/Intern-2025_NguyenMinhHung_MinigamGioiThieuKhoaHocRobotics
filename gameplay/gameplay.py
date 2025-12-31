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

        # --- KHỞI TẠO FINISH MENU ---
        self.finish_menu = FinishMenu(screen)
        # ----------------------------

        self.zone = AssembleZone()
        self.zone.set_state("body", robot_id)

        self.parts = [
            DragItem("head",  (300, 520), self.robot_id),
            DragItem("track", (450, 520), self.robot_id),
            DragItem("arm",   (600, 520), self.robot_id),
            DragItem("power", (750, 520), self.robot_id),
        ]

        # Logic lắp ráp (Tự động tạo tổ hợp)
        self.assembly_logic = {}
        opt_parts = ["arm", "head", "power", "track"]
        def make_state_name(part_list):
            if len(part_list) == 4:
                return f"{self.robot_key}_full_body"
            if not part_list:
                return "body"
            return "body_" + "_".join(sorted(part_list))

        for i in range(5): 
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