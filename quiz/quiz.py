import pygame
import sys
import os
import json
import random
from config import SOUND_SETTINGS 


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class QuizManager:
    def __init__(self, screen_width, screen_height):
        self.sw = screen_width
        self.sh = screen_height
        self.cached_question_surfs = [] 
        self.cached_option_surfs = []

        # ===== FONT =====
        try:
            self.font_q = pygame.font.Font(
                os.path.join("Font", "Mitr", "Mitr-Medium.ttf"), 26
            )
            self.font_a = pygame.font.Font(
                os.path.join("Font", "Mitr", "Mitr-Medium.ttf"), 18
            )
        except:
            self.font_q = pygame.font.SysFont("Arial", 26, bold=True)
            self.font_a = pygame.font.SysFont("Arial", 18, bold=True)

        # ===== BOARD =====
        try:
            raw = pygame.image.load(
                os.path.join("Images", "Board", "board.png")
            ).convert_alpha()
        except:
            raw = pygame.Surface((600, 400))
            raw.fill((50, 50, 50))

        bw = int(self.sw * 0.8)
        bh = int(bw * raw.get_height() / raw.get_width())
        self.board_img = pygame.transform.smoothscale(raw, (bw, bh))
        self.board_rect = self.board_img.get_rect(
            center=(self.sw // 2, self.sh // 2)
        )

        # ===== BUTTONS =====
        self.buttons = []
        labels = ["A", "B", "C", "D"]

        try:
            temp = pygame.image.load(
                os.path.join("Images", "Board", "A_base.png")
            ).convert_alpha()
            btn_w = int(self.board_rect.width * 0.3)
            btn_h = int(btn_w * temp.get_height() / temp.get_width())
        except:
            btn_w, btn_h = 200, 50

        bx, by = self.board_rect.topleft
        bw_board, bh_board = self.board_rect.size

        positions = [
            (bx + int(bw_board * 0.18), by + int(bh_board * 0.48)),
            (bx + int(bw_board * 0.52), by + int(bh_board * 0.48)),
            (bx + int(bw_board * 0.18), by + int(bh_board * 0.68)),
            (bx + int(bw_board * 0.52), by + int(bh_board * 0.68)),
        ]

        for i, label in enumerate(labels):
            imgs = {}
            for state in ["base", "hover", "pressed", "correct", "wrong"]:
                path = os.path.join(
                    "Images", "Board", f"{label}_{state}.png"
                )
                try:
                    img = pygame.image.load(path).convert_alpha()
                    imgs[state] = pygame.transform.smoothscale(
                        img, (btn_w, btn_h)
                    )
                except:
                    surf = pygame.Surface((btn_w, btn_h))
                    if state == "base": surf.fill((100, 100, 100))
                    elif state == "hover": surf.fill((150, 150, 150))
                    elif state == "pressed": surf.fill((80, 80, 80))
                    elif state == "correct": surf.fill((0, 200, 0))
                    elif state == "wrong": surf.fill((200, 0, 0))
                    imgs[state] = surf

            rect = imgs["base"].get_rect(topleft=positions[i])
            self.buttons.append({
                "imgs": imgs,
                "rect": rect,
                "hover": False,
                "pressed": False,
                "state": "base"
            })

        # ===== SOUND =====
        self.snd_correct = None
        self.snd_wrong = None
        self.correct_ch = None
        self.wrong_ch = None

        try:
            self.snd_correct = pygame.mixer.Sound(
                os.path.join("Sound", "correct-choice.mp3")
            )
            self.snd_wrong = pygame.mixer.Sound(
                os.path.join("Sound", "wrong-choice.mp3")
            )

            self.snd_correct.set_volume(0.7)
            self.snd_wrong.set_volume(0.7)

            self.correct_ch = pygame.mixer.Channel(3)
            self.wrong_ch = pygame.mixer.Channel(4)

        except Exception as e:
            print("⚠ Không load được sound quiz:", e)

        # ===== STATE =====
        self.is_active = False
        self.question = None
        self.result_time = None
        self.result_delay = 500
        self.result_value = None
        self.fade_alpha = 0
        self.fading = False

    # =====================================================
    #  OPTIMIZATION HELPERS
    # =====================================================
    def _wrap_text_to_surfaces(self, text, font, max_w, color):
        """Helper: Render text thành danh sách các surface đã wrap (tối đa 2 dòng)"""
        words = text.split()
        lines, cur = [], ""
        surfaces = []

        for w in words:
            test = cur + w + " "
            if font.size(test)[0] <= max_w:
                cur = test
            else:
                lines.append(cur)
                cur = w + " "
                if len(lines) == 2:
                    break

        if len(lines) < 2:
            lines.append(cur)

        # Xử lý cắt bớt nếu dòng quá dài
        while font.size(lines[-1] + "...")[0] > max_w and len(lines[-1]) > 0:
            lines[-1] = lines[-1][:-1]

        if lines[-1].strip() != cur.strip():
            lines[-1] = lines[-1].strip() + "..."

        for line in lines[:2]:
            surfaces.append(font.render(line, True, color))
        return surfaces

    # =====================================================
    def start_quiz(self, data):
        self.question = data
        self.is_active = True
        self.result_time = None
        self.result_value = None
        self.fade_alpha = 0
        self.fading = False

        for b in self.buttons:
            b["state"] = "base"
            b["hover"] = False
            b["pressed"] = False

        # 1. Render Câu hỏi
        max_w_q = int(self.board_rect.width * 0.75)
        self.cached_question_surfs = self._wrap_text_to_surfaces(
            data["question"], self.font_q, max_w_q, WHITE
        )

        # 2. Render Các đáp án
        self.cached_option_surfs = []
        for i, opt_text in enumerate(data["options"]):
            if i >= len(self.buttons): break
            
            btn_rect = self.buttons[i]["rect"]
            padding = int(btn_rect.width * 0.42)
            avail_w = btn_rect.width - padding - 20
            
            surfs = self._wrap_text_to_surfaces(opt_text, self.font_a, avail_w, WHITE)
            self.cached_option_surfs.append(surfs)
        # --------------------------------------------------------

    # =====================================================
    def handle_input(self, event):
        if not self.is_active or self.fading:
            return None

        mouse = pygame.mouse.get_pos()
        hovered = None

        for b in self.buttons:
            b["hover"] = False
            if b["rect"].collidepoint(mouse) and hovered is None:
                b["hover"] = True
                hovered = b

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for b in self.buttons:
                b["pressed"] = False
            if hovered:
                hovered["pressed"] = True

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            for i, b in enumerate(self.buttons):
                if b["pressed"] and b["hover"] and self.result_time is None:
                    correct = i == self.question["correct_index"]

                    # ===== PLAY SOUND (KIỂM TRA SETTING) =====
                    if SOUND_SETTINGS["sfx_on"]:
                        if correct and self.snd_correct:
                            self.correct_ch.play(self.snd_correct)
                        elif not correct and self.snd_wrong:
                            self.wrong_ch.play(self.snd_wrong)
                    # =========================================

                    b["state"] = "correct" if correct else "wrong"
                    if not correct:
                        self.buttons[self.question["correct_index"]]["state"] = "correct"

                    self.result_time = pygame.time.get_ticks()
                    self.result_value = correct

            for b in self.buttons:
                b["pressed"] = False

        return None

    # =====================================================
    def update(self):
        if not self.is_active:
            return None

        now = pygame.time.get_ticks()

        if self.result_time and not self.fading:
            if now - self.result_time >= self.result_delay:
                self.fading = True

        if self.fading:
            self.fade_alpha += 12
            if self.fade_alpha >= 255:
                self.fade_alpha = 255
                self.is_active = False
                self.fading = False
                return self.result_value

        return None

    # =====================================================
    def draw(self, screen):
        if not self.is_active:
            return

        # 1. Vẽ nền tối
        dark = pygame.Surface((self.sw, self.sh))
        dark.set_alpha(180)
        dark.fill(BLACK)
        screen.blit(dark, (0, 0))

        # 2. Vẽ bảng câu hỏi
        screen.blit(self.board_img, self.board_rect)

        # 3. Vẽ câu hỏi
        y = self.board_rect.top + int(self.board_rect.height * 0.38)
        for surf in self.cached_question_surfs:
            rect = surf.get_rect(center=(self.sw // 2, y))
            screen.blit(surf, rect)
            y += 32

        # 4. Vẽ các nút & đáp án
        for i, b in enumerate(self.buttons):
            # Chọn hình ảnh nút
            img = b["imgs"]["base"]
            if b["state"] in ("correct", "wrong"):
                img = b["imgs"][b["state"]]
            elif b["pressed"]:
                img = b["imgs"]["pressed"]
            elif b["hover"]:
                img = b["imgs"]["hover"]

            screen.blit(img, b["rect"])

            # Vẽ text đáp án
            if i < len(self.cached_option_surfs):
                surfs = self.cached_option_surfs[i]
                padding = int(b["rect"].width * 0.42)
                
                # Căn giữa text theo chiều dọc trong nút
                ty = b["rect"].centery - (len(surfs) * 30) // 2
                
                for surf in surfs:
                    screen.blit(surf, (b["rect"].left + padding, ty))
                    ty += 18

        # 5. Hiệu ứng Fade out khi xong
        if self.fading:
            fade = pygame.Surface((self.sw, self.sh))
            fade.set_alpha(self.fade_alpha)
            fade.fill(BLACK)
            screen.blit(fade, (0, 0))
            
    # =====================================================
    def load_question_for_robot(self, robot_id, json_path="questions.json"):
        """Hàm hỗ trợ cũ, giữ lại để tương thích nếu cần gọi trực tiếp"""
        path = os.path.join(BASE_DIR, json_path)
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            pool = data.get(robot_id, [])
            if not pool: return None
            raw = random.choice(pool)
            return {
                "question": raw["question"],
                "options": raw["options"],
                "correct_index": raw["answer"]
            }
        except:
            return None