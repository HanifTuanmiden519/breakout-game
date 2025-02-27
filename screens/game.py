from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from utils.config import get_difficulty  # ใช้ค่าจาก config
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget

class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')

        # แสดงข้อความเริ่มต้น
        self.label = Label(text="Game Screen - Coming Soon!", font_size=24)
        self.layout.add_widget(self.label)

        # ปุ่มกลับไปที่เมนู
        back_btn = Button(text="Back to Menu", size_hint=(1, 0.2))
        back_btn.bind(on_press=self.go_to_menu)
        self.layout.add_widget(back_btn)

        self.add_widget(self.layout)

    def on_pre_enter(self, *args):
        """อัปเดตข้อความเมื่อจะเข้าหน้า GameScreen"""
        # ดึงโหมดที่เลือกจาก config
        difficulty = get_difficulty()
        self.label.text = f"Game Mode: {difficulty.capitalize()}"

    def go_to_menu(self, instance):
        """กลับไปหน้าเมนู"""
        self.manager.current = "menu"

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

    def end_game(self):
        """เกมจบ (แพ้)"""
        print(f"Game Over! Your Score: {self.score}")
    
    def on_touch_move(self, touch):
        """ควบคุมไม้ตี"""
    new_x = touch.x - self.paddle.size[0] / 2
    new_x = max(0, min(Window.width - self.paddle.size[0], new_x))  # ไม่ให้เลยขอบจอ
    self.paddle.pos = (new_x, self.paddle.pos[1])


