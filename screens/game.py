from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Rectangle, Ellipse, Color, Line
from kivy.clock import Clock
from kivy.core.window import Window
from utils.config import get_difficulty

class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game_widget = BreakoutGame(self)
        self.add_widget(self.game_widget)
        
        # UI บนขอบจอ
        self.score_label = Label(text="Score: 0", size_hint=(None, None), pos=(20, Window.height - 40))
        self.lives_label = Label(text="Lives: 3", size_hint=(None, None), pos=(200, Window.height - 40))
        self.back_button = Button(text="Back to Menu", size_hint=(None, None), size=(150, 50), pos=(Window.width - 180, Window.height - 50))
        self.back_button.bind(on_press=self.back_to_menu)
        
        self.add_widget(self.score_label)
        self.add_widget(self.lives_label)
        self.add_widget(self.back_button)
    
    def on_pre_enter(self, *args):
        self.game_widget.start_game()
        self.update_labels()
        
    def update_labels(self):
        self.score_label.text = f"Score: {self.game_widget.score}"
        self.lives_label.text = f"Lives: {self.game_widget.lives}"
        
    def back_to_menu(self, instance):
        self.manager.current = "menu"

class BreakoutGame(Widget):
    def __init__(self, game_screen, **kwargs):
        super().__init__(**kwargs)
        self.game_screen = game_screen
        self.ball = None
        self.paddle = None
        self.blocks = []
        self.dx = 4
        self.dy = 4
        self.lives = 3
        self.score = 0
        self.running = False
        self.setup_game()
        
    def setup_game(self):
        self.canvas.clear()
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
            Color(0, 0, 0)
            Rectangle(size=Window.size)
        
            # เส้นคั่นระหว่าง UI กับเกม
            Color(1, 1, 1)
            Line(points=[0, Window.height - 60, Window.width, Window.height - 60], width=2)
        
            Color(1, 1, 1)
            self.paddle = Rectangle(
                size=(settings["paddle_size"], 20),
                pos=(Window.width / 2 - settings["paddle_size"] / 2, 50)
            )
        
            Color(1, 1, 1)
            self.ball = Ellipse(size=(20, 20), pos=(Window.width / 2, Window.height / 2))
        
            self.blocks = []
            Color(1, 1, 1)
            rows = 5
            cols = 7
            block_width = Window.width / cols
            block_height = 30
            block_start_y = Window.height - 90  # บล็อกเริ่มต้นใต้เส้นคั่น

            for row in range(rows):
                for col in range(cols):
                    block = Rectangle(size=(block_width - 5, block_height - 5), 
                                      pos=(col * block_width, block_start_y - (row * block_height)))
                    self.blocks.append(block)
        
        self.running = True
    
    def start_game(self):
        self.setup_game()
        Clock.schedule_interval(self.update, 1 / 60)
        
    def update(self, dt):
        if not self.running:
            return

        self.ball.pos = (self.ball.pos[0] + self.dx, self.ball.pos[1] + self.dy)

        if self.ball.pos[0] <= 0 or self.ball.pos[0] + self.ball.size[0] >= Window.width:
            self.dx *= -1

        if self.ball.pos[1] + self.ball.size[1] >= Window.height:
            self.dy *= -1
            
        if self.ball.pos[1] <= self.paddle.pos[1] + self.paddle.size[1] and \
           self.paddle.pos[0] <= self.ball.pos[0] <= self.paddle.pos[0] + self.paddle.size[0]:
            self.dy *= -1    
        
        for block in self.blocks[:]:
            if block.pos[0] <= self.ball.pos[0] <= block.pos[0] + block.size[0] and \
               block.pos[1] <= self.ball.pos[1] <= block.pos[1] + block.size[1]:
                self.blocks.remove(block)
                self.canvas.remove(block)
                self.dy *= -1
                self.score += 10
                self.game_screen.update_labels()
        
        if self.ball.pos[1] <= 0:
            self.lives -= 1
            self.game_screen.update_labels()
            if self.lives > 0:
                self.ball.pos = (Window.width / 2, Window.height / 2)
                self.dy *= -1
            else:
                self.running = False
                Clock.unschedule(self.update)
                self.end_game()
                
    def end_game(self):
        print(f"Game Over! Your Score: {self.score}")
    
    def on_touch_move(self, touch):
        new_x = touch.x - self.paddle.size[0] / 2
        new_x = max(0, min(Window.width - self.paddle.size[0], new_x))
        self.paddle.pos = (new_x, self.paddle.pos[1])