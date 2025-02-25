from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from utils.config import set_difficulty  # สำหรับการตั้งโหมด

class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', spacing=10, padding=50)

        easy_btn = Button(text="Easy", font_size=24, size_hint=(1, 0.2))
        easy_btn.bind(on_press=lambda x: self.select_mode("easy"))
        
        medium_btn = Button(text="Medium", font_size=24, size_hint=(1, 0.2))
        medium_btn.bind(on_press=lambda x: self.select_mode("medium"))

        hard_btn = Button(text="Hard", font_size=24, size_hint=(1, 0.2))
        hard_btn.bind(on_press=lambda x: self.select_mode("hard"))

        layout.add_widget(easy_btn)
        layout.add_widget(medium_btn)
        layout.add_widget(hard_btn)
        self.add_widget(layout)

    def select_mode(self, mode):
        """เลือกโหมดและไปหน้าเกม"""
        set_difficulty(mode)
        self.manager.current = "game"
