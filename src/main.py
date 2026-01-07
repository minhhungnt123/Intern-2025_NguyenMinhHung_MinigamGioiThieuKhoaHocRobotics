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
try: pygame.mixer.init()
except: pass

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Robotics Assembly Game")
clock = pygame.time.Clock()

# --- XỬ LÝ NHẠC NỀN ---
bgm_path = os.path.join(PROJECT_ROOT, "Sound", "bgm.mp3")
if os.path.exists(bgm_path):
    try:
        pygame.mixer.music.load(bgm_path)
        pygame.mixer.music.set_volume(0.5) 
        if SOUND_SETTINGS["bgm_on"]: pygame.mixer.music.play(-1)
    except Exception as e: print("Lỗi nhạc:", e)

# ===== INIT OBJECTS =====
state = GameState.MAIN_MENU

main_menu = Menu(screen)
robot_menu = RobotSelectMenu(screen)
table_bg = TableBackground()

# Các biến dynamic
design_plan = None
gameplay = None
selected_robot = None

# ===== MAIN LOOP =====
running = True
while running:
    clock.tick(FPS)
    events = pygame.event.get() 

    for event in events:
        if event.type == pygame.QUIT:
            running = False

        # --- EVENT DISPATCHER ---
        if state == GameState.MAIN_MENU:
            action = main_menu.handle_event(event)
            if action == "toggle_bgm":
                if SOUND_SETTINGS["bgm_on"]:
                    if not pygame.mixer.music.get_busy(): pygame.mixer.music.play(-1)
                    else: pygame.mixer.music.unpause()
                else: pygame.mixer.music.stop()

        elif state == GameState.ROBOT_MENU:
            action = robot_menu.handle_event(event)
            if action == "back":
                state = GameState.MAIN_MENU
                main_menu.state = "INTRO"
                main_menu.alpha = 0

        elif state == GameState.GAME:
            action = gameplay.handle_event(event)
            if action == "restart":
                gameplay = Gameplay(screen, selected_robot, design_plan)
            elif action == "home":
                state = GameState.MAIN_MENU
                main_menu.state = "INTRO"
                main_menu.alpha = 0
                if SOUND_SETTINGS["bgm_on"] and not pygame.mixer.music.get_busy():
                    pygame.mixer.music.play(-1)
            elif action in ["robot_1", "robot_2", "robot_3"]:
                selected_robot = action
                gameplay = Gameplay(screen, selected_robot, design_plan)

    # --- DRAW BACKGROUND ---
    if state in (GameState.MAIN_MENU, GameState.ROBOT_MENU):
        table_bg.update()
        table_bg.draw(screen)
    elif state == GameState.DESIGN_PLAN:
        table_bg.draw(screen)

    # --- STATE LOGIC & DRAW ---
    if state == GameState.MAIN_MENU:
        result = main_menu.update()
        main_menu.draw()
        if result == "START_GAME":
            state = GameState.ROBOT_MENU
            robot_menu.selected_robot = None

    elif state == GameState.ROBOT_MENU:
        robot_menu.update()
        robot_menu.draw()
        result = robot_menu.get_selected_robot()
        if result:
            selected_robot = result
            design_plan = DesignPlanBackground()
            state = GameState.DESIGN_PLAN

    elif state == GameState.DESIGN_PLAN:
        design_plan.update()
        design_plan.draw(screen)
        if design_plan.done:
            pygame.display.flip() 
            gameplay = Gameplay(screen, selected_robot, design_plan)
            state = GameState.GAME

    elif state == GameState.GAME:
        gameplay.update()
        gameplay.draw()

    pygame.display.flip()

pygame.quit()