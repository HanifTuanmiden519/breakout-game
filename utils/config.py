# ตั้งค่าโหมดต่างๆ
difficulty_settings = {
    "easy": {"speed": 2, "paddle_size": 150, "lives": 5},
    "medium": {"speed": 4, "paddle_size": 120, "lives": 3},
    "hard": {"speed": 6, "paddle_size": 100, "lives": 2}
}

# โหมดเริ่มต้น
current_difficulty = "medium"

def set_difficulty(mode):
    """ตั้งค่าโหมด"""
    global current_difficulty
    current_difficulty = mode

def get_difficulty():
    """ดึงข้อมูลโหมดปัจจุบัน"""
    return current_difficulty
