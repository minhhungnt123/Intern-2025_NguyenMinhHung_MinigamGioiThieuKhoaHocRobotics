import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# --- MÀU SẮC ---
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_GOLD = (255, 215, 0)
COLOR_PANEL_BG = (50, 50, 70)
COLOR_PANEL_BORDER = (255, 255, 255)

SOUND_SETTINGS = {
    "bgm_on": True,
    "sfx_on": True  
}

# --- GAME STATES  ---
class GameState:
    MAIN_MENU = "main_menu"
    ROBOT_MENU = "robot_menu"
    DESIGN_PLAN = "design_plan"
    GAME = "game"