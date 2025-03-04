from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Rectangle, Color
from kivy.core.window import Window
from utils.config import set_difficulty, get_difficulty

class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # เพิ่มพื้นหลัง
        with self.canvas.before:
            #พื้นหลังสีและภาพเลือกได้โดยเอา # ออก
            #Color(0.9, 0.9, 0.9, 1)
            self.background = Rectangle(source='image/bg start.jpg', pos=self.pos, size=Window.size)
            
        self.bind(pos=self.update_background, size=self.update_background)

        layout = BoxLayout(orientation='vertical', spacing=10, padding=50)

        # สร้าง Label สำหรับแสดงข้อความ 'Breakout Game'
        title_game = Label(text="Breakout Game", font_size=48)
        layout.add_widget(title_game)
        
        # ปุ่ม 'Start Game'
        start_btn = Button(text="Start Game", font_size=24, size_hint=(1, 0.2))
        start_btn.bind(on_press=self.start_game)
        layout.add_widget(start_btn)
        
        
        
        # สร้าง BoxLayout สำหรับปุ่ม 'Previous' และ 'Next'
        arrows_layout = BoxLayout(size_hint=(1, 0.2))
        # ใช้ปุ่ม 'Previous' แทนลูกศรซ้าย
        prev_btn = Button(text="Previous", size_hint=(0.3, 1),
                  background_color=(1, 1, 1, 0.3),  # กำหนดสีเป็นโปร่งใส
                  background_normal='')
        prev_btn.bind(on_press=self.change_difficulty_left)

        # สร้าง Label สำหรับแสดงความยาก
        self.label = Label(text=f"{get_difficulty().capitalize()}", font_size=24)
        
        # ใช้ปุ่ม 'Next' แทนลูกศรขวา
        next_btn = Button(text="Next", size_hint=(0.3, 1),
                  background_color=(1, 1, 1, 0.3),  # กำหนดสีเป็นโปร่งใส
                  background_normal='')
        next_btn.bind(on_press=self.change_difficulty_right)

        # เพิ่ม widget ลงใน layout แนวนอน
        arrows_layout.add_widget(prev_btn)
        arrows_layout.add_widget(self.label)  # ให้ Label อยู่ตรงกลาง
        arrows_layout.add_widget(next_btn)

        layout.add_widget(arrows_layout)

        self.add_widget(layout)

    def update_background(self, *args):
        self.background.pos = self.pos
        self.background.size = self.size

    def change_difficulty_left(self, instance):
        current_difficulty = get_difficulty()
        if current_difficulty == "easy":
            set_difficulty("hard")
        elif current_difficulty == "medium":
            set_difficulty("easy")
        elif current_difficulty == "hard":
            set_difficulty("medium")
        
        self.update_difficulty_label()

    def change_difficulty_right(self, instance):
        current_difficulty = get_difficulty()
        if current_difficulty == "easy":
            set_difficulty("medium")
        elif current_difficulty == "medium":
            set_difficulty("hard")
        elif current_difficulty == "hard":
            set_difficulty("easy")
        
        self.update_difficulty_label()

    def update_difficulty_label(self):
        difficulty = get_difficulty()
        self.label.text = f" {difficulty.capitalize()}"

    def start_game(self, instance):
        self.manager.current = "game"
