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
            # ตั้งค่าสีพื้นหลัง (สีเทาอ่อน)
            Color(0.9, 0.9, 0.9, 1)
            # วาดสี่เหลี่ยมให้เต็มหน้าจอ
            self.background = Rectangle(pos=self.pos, size=Window.size)
            
        layout = BoxLayout(orientation='vertical', spacing=10, padding=50)

        self.label = Label(text=f"Select Game Mode: {get_difficulty().capitalize()}", font_size=24)
        layout.add_widget(self.label)

        arrows_layout = BoxLayout(size_hint=(1, 0.2))
        
        # ใช้ปุ่ม 'Previous' แทนลูกศรซ้าย
        prev_btn = Button(text="Previous", size_hint=(0.3, 1))
        prev_btn.bind(on_press=self.change_difficulty_left)

        # ใช้ปุ่ม 'Next' แทนลูกศรขวา
        next_btn = Button(text="Next", size_hint=(0.3, 1))
        next_btn.bind(on_press=self.change_difficulty_right)

        arrows_layout.add_widget(prev_btn)
        arrows_layout.add_widget(next_btn)

        layout.add_widget(arrows_layout)

        start_btn = Button(text="Start Game", font_size=24, size_hint=(1, 0.2))
        start_btn.bind(on_press=self.start_game)

        layout.add_widget(start_btn)
        self.add_widget(layout)

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
        self.label.text = f"Select Game Mode: {difficulty.capitalize()}"

    def start_game(self, instance):
        self.manager.current = "game"
