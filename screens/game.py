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

        # UI elements with dynamic positioning
        self.score_label = Label(
            text="Score: 0", size_hint=(None, None), size=(150, 30)
        )
        self.lives_label = Label(
            text="Lives: 3", size_hint=(None, None), size=(150, 30)
        )
        self.back_button = Button(
            text="Back to Menu", size_hint=(None, None), size=(150, 50)
        )

        self.back_button.bind(on_press=self.back_to_menu)

        self.add_widget(self.score_label)
        self.add_widget(self.lives_label)
        self.add_widget(self.back_button)

        Window.bind(on_resize=self.update_ui_positions)

    def on_pre_enter(self, *args):
        self.game_widget.start_game()
        self.update_labels()

    def update_labels(self):
        self.score_label.text = f"Score: {self.game_widget.score}"
        self.lives_label.text = f"Lives: {self.game_widget.lives}"

    def update_ui_positions(self, instance, width, height):
        self.score_label.pos = (20, height - 40)
        self.lives_label.pos = (200, height - 40)
        self.back_button.pos = (width - 180, height - 50)

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

        Window.bind(on_resize=self.update_game_elements)

        Window.bind(on_key_down=self.on_key_down)

    def setup_game(self):
        self.canvas.clear()
        difficulty = get_difficulty()
        settings = {
            "easy": {"speed": 4, "paddle_size": 150, "lives": 5},
            "medium": {"speed": 6, "paddle_size": 120, "lives": 3},
            "hard": {"speed": 8, "paddle_size": 100, "lives": 2},
        }[difficulty]

        self.dx = settings["speed"]
        self.dy = settings["speed"]
        self.lives = settings["lives"]

        with self.canvas:
            Color(0, 0, 0)
            Rectangle(size=Window.size)

            # Line separating UI from game
            Color(1, 1, 1)
            Line(
                points=[0, Window.height - 60, Window.width, Window.height - 60],
                width=2,
            )

            # Paddle (centered horizontally)
            Color(1, 1, 1)
            self.paddle = Rectangle(
                size=(settings["paddle_size"], 20),
                pos=(Window.width / 2 - settings["paddle_size"] / 2, 50),
            )

            # Ball (centered on screen)
            Color(1, 1, 1)
            self.ball = Ellipse(
                size=(20, 20), pos=(Window.width / 2, Window.height / 2)
            )

            self.blocks = []
            Color(1, 1, 1)
            rows = 5
            cols = 7
            block_width = Window.width / cols
            block_height = 30
            block_start_y = Window.height - 90  # Starting below the separator line

            for row in range(rows):
                for col in range(cols):
                    block = Rectangle(
                        size=(block_width - 5, block_height - 5),
                        pos=(col * block_width, block_start_y - (row * block_height)),
                    )
                    self.blocks.append(block)

        self.running = True

    def update_game_elements(self, instance, width, height):
        # Update paddle position to be centered
        paddle_size = self.paddle.size[0]  # Keep original paddle size
        self.paddle.pos = (width / 2 - paddle_size / 2, self.paddle.pos[1])

        # Adjust block grid based on the new window size
        block_width = width / 7  # Adjust based on number of columns
        block_height = 30
        block_start_y = height - 90

        for row in range(5):  # 5 rows of blocks
            for col in range(7):  # 7 columns of blocks
                block = self.blocks[row * 7 + col]
                block.pos = (col * block_width, block_start_y - (row * block_height))

    def start_game(self):
        self.setup_game()
        Clock.schedule_interval(self.update, 1 / 60)

    def update(self, dt):
        if not self.running:
            return

        self.ball.pos = (self.ball.pos[0] + self.dx, self.ball.pos[1] + self.dy)

        if (
            self.ball.pos[0] <= 0
            or self.ball.pos[0] + self.ball.size[0] >= Window.width
        ):
            self.dx *= -1

        if self.ball.pos[1] + self.ball.size[1] >= Window.height:
            self.dy *= -1

        if (
            self.ball.pos[1] <= self.paddle.pos[1] + self.paddle.size[1]
            and self.paddle.pos[0]
            <= self.ball.pos[0]
            <= self.paddle.pos[0] + self.paddle.size[0]
        ):
            self.dy *= -1

        for block in self.blocks[:]:
            if (
                block.pos[0] <= self.ball.pos[0] <= block.pos[0] + block.size[0]
                and block.pos[1] <= self.ball.pos[1] <= block.pos[1] + block.size[1]
            ):
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
        self.running = False
        Clock.unschedule(self.update)

        self.show_game_over_message()

    def show_game_over_message(self):
        game_over_label = Label(
            text="Game Over. back to menu!",
            font_size=50,
            size_hint=(None, None),
            size=(300, 100),
            color=(1, 0, 0, 1),
            pos=(Window.width / 2 - 150, Window.height / 2),
        )
        self.add_widget(game_over_label)

        # รอ 3 วินาทีก่อนกลับไปเมนู
        Clock.schedule_once(lambda dt: self.game_screen.manager.current == "menu", 3)

    def on_touch_move(self, touch):
        new_x = touch.x - self.paddle.size[0] / 2
        new_x = max(0, min(Window.width - self.paddle.size[0], new_x))
        self.paddle.pos = (new_x, self.paddle.pos[1])


    def on_key_down(self, window, key, scancode, codepoint, modifier):
        if codepoint == "a":
            self.move_paddle_left()
        elif codepoint == "d":
            self.move_paddle_right()
