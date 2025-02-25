from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from screens.menu import MenuScreen
from screens.settings import SettingsScreen
from screens.game import GameScreen

class BreakoutApp(App):
    def build(self):
        # สร้าง ScreenManager
        sm = ScreenManager()

        # เพิ่มหน้าต่างๆ ลงใน ScreenManager
        sm.add_widget(MenuScreen(name="menu"))
        sm.add_widget(SettingsScreen(name="settings"))
        sm.add_widget(GameScreen(name="game"))

        return sm

if __name__ == "__main__":
    BreakoutApp().run()
