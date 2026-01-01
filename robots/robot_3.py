# robots/robot_1.py
from robots.robot_base import RobotBase

class Robot1(RobotBase):
    def __init__(self):
        super().__init__()
        # Cấu hình ID (Quan trọng để tìm thư mục ảnh)
        self.id = "Robot_3" 

    # --- CẤU HÌNH LOGIC LẮP RÁP ---
    ASSEMBLY_LOGIC = {
        "body": {
            "head": "head_body",
            "track": "body_track"
        },
        "head_body": {
            "track": "head_body_track",
            "arm": "head_body_arm"
        },
        "body_track": {
            "head": "head_body_track",
            "arm": "body_track_arm"
        },
        "head_body_track": {
            "arm": "head_body_track_arm"
        },
        "head_body_track_arm": {
            "power": "head_body_track_power"
        }
    }

    # --- DANH SÁCH BỘ PHẬN CẦN HIỂN THỊ ---
    # Toạ độ (x, y) phải nằm trong màn hình (1280x720)
    PARTS_LIST = [
        {"name": "head",  "pos": (300, 500)},
        {"name": "track", "pos": (500, 500)},
        {"name": "arm",   "pos": (700, 500)},
        {"name": "power", "pos": (900, 500)},
    ]

    INITIAL_STATE = "body"
    FULL_BODY_IMAGE = "robot_3_full_body.png"