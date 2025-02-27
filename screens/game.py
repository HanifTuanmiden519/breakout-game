from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Ellipse, Color
from kivy.clock import Clock
from kivy.core.window import Window
from utils.config import get_difficulty

class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game_widget = BreakoutGame()
        self.add_widget(self.game_widget)

    def on_pre_enter(self, *args):
        """อัปเดตค่าตามโหมดที่เลือกเมื่อเข้าหน้าเกม"""
        self.game_widget.start_game()

class BreakoutGame(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ball = None
        self.paddle = None
        self.blocks = []
        self.dx = 4  # ทิศทางการเคลื่อนที่แนวนอนของลูกบอล
        self.dy = 4  # ทิศทางการเคลื่อนที่แนวตั้งของลูกบอล
        self.lives = 3
        self.score = 0
        self.running = False
        self.setup_game()
        
    def setup_game(self):
        self.canvas.clear()
    # กำหนดค่าความยาก
        difficulty = get_difficulty()
        settings = {
            "easy": {"speed": 2, "paddle_size": 150, "lives": 5},
            "medium": {"speed": 4, "paddle_size": 120, "lives": 3},
            "hard": {"speed": 6, "paddle_size": 100, "lives": 2}
        }[difficulty]
    
        self.dx = settings["speed"]
        self.dy = settings["speed"]
        self.lives = settings["lives"]
    
        with self.canvas:
            # วาดพื้นหลัง
            Color(0, 0, 0)
            Rectangle(size=Window.size)
        
            # วาดไม้ตี
            Color(0, 1, 0)
            self.paddle = Rectangle(
            size=(settings["paddle_size"], 20),
            pos=(Window.width / 2 - settings["paddle_size"] / 2, 50)
            )
        
            # วาดลูกบอล
            Color(1, 0, 0)
            self.ball = Ellipse(size=(20, 20), pos=(Window.width / 2, Window.height / 2))
        
            # วาดบล็อก
            self.blocks = []
            Color(0, 0, 1)
            rows = 5
            cols = 7
            block_width = Window.width / cols
            block_height = 30

            for row in range(rows):
                for col in range(cols):
                    block = Rectangle(size=(block_width - 5, block_height - 5), 
                                      pos=(col * block_width, Window.height - (row + 1) * block_height))
                    self.blocks.append(block)

        self.running = True
    def start_game(self):
        """เริ่มเกมใหม่"""
        self.setup_game()
        Clock.schedule_interval(self.update, 1 / 60)
        
    def update(self, dt):
        """อัปเดตการเคลื่อนที่ของลูกบอล"""
        if not self.running:
            return

        # อัปเดตตำแหน่งลูกบอล
        self.ball.pos = (self.ball.pos[0] + self.dx, self.ball.pos[1] + self.dy)

        # ขอบจอซ้าย-ขวา
        if self.ball.pos[0] <= 0 or self.ball.pos[0] + self.ball.size[0] >= Window.width:
            self.dx *= -1

        # ขอบจอบน
        if self.ball.pos[1] + self.ball.size[1] >= Window.height:
            self.dy *= -1
            
        # ตรวจสอบการชนกับไม้ตี
        if self.ball.pos[1] <= self.paddle.pos[1] + self.paddle.size[1] and \
           self.paddle.pos[0] <= self.ball.pos[0] <= self.paddle.pos[0] + self.paddle.size[0]:
            self.dy *= -1    
                
    def end_game(self):
        """เกมจบ (แพ้)"""
        print(f"Game Over! Your Score: {self.score}")
    
    def on_touch_move(self, touch):
        """ควบคุมไม้ตี"""
        new_x = touch.x - self.paddle.size[0] / 2
        new_x = max(0, min(Window.width - self.paddle.size[0], new_x))  # ไม่ให้เลยขอบจอ
        self.paddle.pos = (new_x, self.paddle.pos[1])

