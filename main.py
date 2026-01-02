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
        if SOUND_SETTINGS["bgm_on"]:
            pygame.mixer.music.play(-1)
        print(" Đã load nhạc nền thành công!")
    except Exception as e:
        print(" Lỗi khi load nhạc:", e)
else:
    print(f" Không tìm thấy file nhạc tại: {bgm_path}")

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
    events = pygame.event.get() 
    for event in events:
        if event.type == pygame.QUIT:
            running = False

        # --- 1. MAIN MENU EVENTS ---
        if state == STATE_MAIN_MENU:
            action = main_menu.handle_event(event)
            if action == "toggle_bgm":
                if SOUND_SETTINGS["bgm_on"]:
                    if not pygame.mixer.music.get_busy(): pygame.mixer.music.play(-1)
                    else: pygame.mixer.music.unpause()
                else:
                    pygame.mixer.music.stop()

        # --- 2. ROBOT MENU EVENTS ---
        elif state == STATE_ROBOT_MENU:
            action = robot_menu.handle_event(event)
            if action == "back":
                state = STATE_MAIN_MENU
                main_menu.state = "INTRO"
                main_menu.alpha = 0

        # --- 3. GAMEPLAY EVENTS ---
        elif state == STATE_GAME:
            # Gameplay xử lý event và trả về action
            action = gameplay.handle_event(event)
            
            # --- CÁC TRƯỜNG HỢP XỬ LÝ ---
            
            # 1. Chơi lại (Restart)
            if action == "restart":
                print("🔄 Restarting Level...")
                gameplay = Gameplay(screen, selected_robot, design_plan)
                
            # 2. Về trang chủ (Home)
            elif action == "home":
                print("Going Home...")
                state = STATE_MAIN_MENU
                main_menu.state = "INTRO"
                main_menu.alpha = 0
                if SOUND_SETTINGS["bgm_on"] and not pygame.mixer.music.get_busy():
                    pygame.mixer.music.play(-1)

            # 3. MỚI: Chuyển robot từ Menu Chiến Thắng
            elif action in ["robot_1", "robot_2", "robot_3"]:
                print(f"Switching to {action}...")
                selected_robot = action
                gameplay = Gameplay(screen, selected_robot, design_plan)


    # ================= DRAW BACKGROUND =================
    if state in (STATE_MAIN_MENU, STATE_ROBOT_MENU):
        table_bg.update()
        table_bg.draw(screen)
    elif state == STATE_DESIGN_PLAN:
        table_bg.draw(screen)

    # ================= STATE LOGIC & DRAW =================
    
    # --- 1. MAIN MENU ---
    if state == STATE_MAIN_MENU:
        result = main_menu.update()
        main_menu.draw()
        if result == "START_GAME":
            state = STATE_ROBOT_MENU
            robot_menu.selected_robot = None

    # --- 2. ROBOT SELECT MENU ---
    elif state == STATE_ROBOT_MENU:
        robot_menu.update()
        robot_menu.draw()
        result = robot_menu.get_selected_robot()
        if result:
            selected_robot = result
            design_plan = DesignPlanBackground()
            state = STATE_DESIGN_PLAN

    # --- 3. DESIGN PLAN (Transition) ---
    elif state == STATE_DESIGN_PLAN:
        design_plan.update()
        design_plan.draw(screen)
        
        if design_plan.done:
            pygame.display.flip() 
            gameplay = Gameplay(screen, selected_robot, design_plan)
            state = STATE_GAME

    # --- 4. GAMEPLAY ---
    elif state == STATE_GAME:
        gameplay.update()
        gameplay.draw()

    pygame.display.flip()

pygame.quit()