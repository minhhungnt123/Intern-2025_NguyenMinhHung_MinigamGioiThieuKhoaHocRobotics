import pygame
from config import *
import os

from menu.main_menu import Menu
from menu.robot_menu import RobotSelectMenu

from background.table_background import TableBackground
from background.design_plan_background import DesignPlanBackground

from gameplay.gameplay import Gameplay


pygame.init()
try:
    pygame.mixer.init()
except:
    pass
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Robotics Assembly Game")
clock = pygame.time.Clock()

bgm_path = os.path.join(PROJECT_ROOT, "Sound", "bgm.mp3")

if os.path.exists(bgm_path):
    try:
        # Load nhạc
        pygame.mixer.music.load(bgm_path)
        
        # Chỉnh âm lượng (0.0 đến 1.0) - Đừng để to quá át tiếng hiệu ứng
        pygame.mixer.music.set_volume(0.5) 
        
        # Phát nhạc lặp vô tận (-1 nghĩa là loop forever)
        pygame.mixer.music.play(-1)
        
        print("♫ Đã phát nhạc nền thành công!")
    except Exception as e:
        print("⚠ Lỗi khi load nhạc:", e)
else:
    print(f"❌ Không tìm thấy file nhạc tại: {bgm_path}")

# ===== STATES =====
STATE_MAIN_MENU = "main_menu"
STATE_ROBOT_MENU = "robot_menu"
STATE_DESIGN_PLAN = "design_plan"
STATE_GAME = "game"

state = STATE_MAIN_MENU

# ===== OBJECTS =====
main_menu = Menu(screen)
robot_menu = RobotSelectMenu(screen)

table_bg = TableBackground()
design_plan = None
gameplay = None

selected_robot = None

running = True
while running:
    clock.tick(FPS)

    # ================= EVENT =================
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if state == STATE_MAIN_MENU:
            main_menu.handle_event(event)

        elif state == STATE_ROBOT_MENU:
            robot_menu.handle_event(event)

        elif state == STATE_GAME:
            gameplay.handle_event(event)

    # ================= DRAW BACKGROUND =================
    if state in (STATE_MAIN_MENU, STATE_ROBOT_MENU):
        table_bg.update()
        table_bg.draw(screen)

    elif state == STATE_DESIGN_PLAN:
        table_bg.draw(screen)   # nền cũ phía sau

    # ================= STATE LOGIC =================
    if state == STATE_MAIN_MENU:
        result = main_menu.update()
        main_menu.draw()

        if result == "START_GAME":
            state = STATE_ROBOT_MENU

    elif state == STATE_ROBOT_MENU:
        robot_menu.update()
        robot_menu.draw()

        result = robot_menu.get_selected_robot()
        if result:
            selected_robot = result
            design_plan = DesignPlanBackground()
            state = STATE_DESIGN_PLAN

    elif state == STATE_DESIGN_PLAN:
        table_bg.draw(screen)
        design_plan.update()
        design_plan.draw(screen)

        if design_plan.done:
            gameplay = Gameplay(screen, selected_robot, design_plan)
            state = STATE_GAME


    elif state == STATE_GAME:
        gameplay.update()
        gameplay.draw()

    pygame.display.flip()

pygame.quit()
