import pygame
import os
from config import *

from menu.main_menu import Menu
from menu.robot_menu import RobotSelectMenu

from background.table_background import TableBackground
from background.design_plan_background import DesignPlanBackground

from gameplay.gameplay import Gameplay

# --- KHỞI TẠO PYGAME ---
pygame.init()
try:
    pygame.mixer.init()
except:
    pass

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Robotics Assembly Game")
clock = pygame.time.Clock()

# --- XỬ LÝ NHẠC NỀN (BGM) ---
bgm_path = os.path.join(PROJECT_ROOT, "Sound", "bgm.mp3")

if os.path.exists(bgm_path):
    try:
        pygame.mixer.music.load(bgm_path)
        pygame.mixer.music.set_volume(0.5) 
        
        # Chỉ phát nhạc nếu trong Config đang bật (mặc định True)
        if SOUND_SETTINGS["bgm_on"]:
            pygame.mixer.music.play(-1) # Loop vô hạn
            
        print("♫ Đã load nhạc nền thành công!")
    except Exception as e:
        print("⚠ Lỗi khi load nhạc:", e)
else:
    print(f"❌ Không tìm thấy file nhạc tại: {bgm_path}")

# ===== DEFINES STATES =====
STATE_MAIN_MENU = "main_menu"
STATE_ROBOT_MENU = "robot_menu"
STATE_DESIGN_PLAN = "design_plan"
STATE_GAME = "game"

state = STATE_MAIN_MENU

# ===== INIT OBJECTS =====
main_menu = Menu(screen)
robot_menu = RobotSelectMenu(screen)

table_bg = TableBackground()
design_plan = None
gameplay = None

selected_robot = None

# ===== MAIN LOOP =====
running = True
while running:
    clock.tick(FPS)

    # ================= EVENT HANDLING =================
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # --- 1. MAIN MENU EVENTS ---
        if state == STATE_MAIN_MENU:
            action = main_menu.handle_event(event)
            
            # Xử lý bật/tắt nhạc từ Setting Menu
            if action == "toggle_bgm":
                if SOUND_SETTINGS["bgm_on"]:
                    if not pygame.mixer.music.get_busy():
                        pygame.mixer.music.play(-1)
                    else:
                        pygame.mixer.music.unpause()
                else:
                    pygame.mixer.music.stop()

        # --- 2. ROBOT MENU EVENTS ---
        elif state == STATE_ROBOT_MENU:
            action = robot_menu.handle_event(event)
            
            # Nút Back (Home Icon) quay về menu chính
            if action == "back":
                state = STATE_MAIN_MENU
                main_menu.state = "INTRO" # Reset hiệu ứng fade
                main_menu.alpha = 0

        # --- 3. GAMEPLAY EVENTS ---
        elif state == STATE_GAME:
            action = gameplay.handle_event(event)
            
            # Nút Restart (chơi lại màn hiện tại)
            if action == "restart":
                print("🔄 Restarting Level...")
                gameplay = Gameplay(screen, selected_robot, design_plan)
                
            # Nút Home (quay về menu chính)
            elif action == "home":
                print("🏠 Going Home...")
                state = STATE_MAIN_MENU
                main_menu.state = "INTRO"
                main_menu.alpha = 0
                
                # Reset nhạc nền nếu đang bị hiệu ứng game đè (tùy chọn)
                if SOUND_SETTINGS["bgm_on"] and not pygame.mixer.music.get_busy():
                    pygame.mixer.music.play(-1)

    # ================= DRAW BACKGROUND =================
    # Vẽ nền bàn gỗ cho các menu
    if state in (STATE_MAIN_MENU, STATE_ROBOT_MENU):
        table_bg.update()
        table_bg.draw(screen)

    # Vẽ nền bàn gỗ tĩnh phía sau bản vẽ thiết kế
    elif state == STATE_DESIGN_PLAN:
        table_bg.draw(screen)

    # ================= STATE LOGIC & DRAW =================
    
    # --- 1. MAIN MENU ---
    if state == STATE_MAIN_MENU:
        result = main_menu.update()
        main_menu.draw()

        if result == "START_GAME":
            state = STATE_ROBOT_MENU
            robot_menu.selected_robot = None # Reset lựa chọn cũ

    # --- 2. ROBOT SELECT MENU ---
    elif state == STATE_ROBOT_MENU:
        robot_menu.update()
        robot_menu.draw()

        # Kiểm tra xem người chơi đã chọn robot chưa
        result = robot_menu.get_selected_robot()
        if result:
            selected_robot = result
            # Chuyển sang màn hình xem bản vẽ
            design_plan = DesignPlanBackground()
            state = STATE_DESIGN_PLAN

    # --- 3. DESIGN PLAN (Transition) ---
    elif state == STATE_DESIGN_PLAN:
        design_plan.update()
        design_plan.draw(screen)

        # Khi xem xong bản vẽ -> Vào game chính
        if design_plan.done:
            gameplay = Gameplay(screen, selected_robot, design_plan)
            state = STATE_GAME

    # --- 4. GAMEPLAY ---
    elif state == STATE_GAME:
        gameplay.update()
        gameplay.draw()

    pygame.display.flip()

pygame.quit()