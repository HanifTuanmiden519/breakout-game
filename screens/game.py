from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from utils.config import get_difficulty  # ใช้ค่าจาก config

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
