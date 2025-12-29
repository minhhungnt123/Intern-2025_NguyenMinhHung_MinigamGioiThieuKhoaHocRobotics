from robots.robot_base import RobotBase

class Robot1(RobotBase):
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
            "power": "head_body_track_power" # Hoàn thiện
        }
    }

    # Danh sách các bộ phận rời nằm ở bên dưới
    PARTS_LIST = [
        {"name": "head", "pos": (300, 600)},
        {"name": "track", "pos": (500, 600)},
        {"name": "arm",   "pos": (700, 600)},
        {"name": "power", "pos": (900, 600)},
    ]

    INITIAL_STATE = "body"                # Trạng thái bắt đầu (chỉ có thân)
    FULL_BODY_IMAGE = "robot_1_full_body.png" # Ảnh mẫu hoàn chỉnh