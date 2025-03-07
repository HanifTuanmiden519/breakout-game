from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Rectangle, Ellipse, Color, Line
from kivy.clock import Clock
from kivy.core.window import Window
from utils.config import get_difficulty
from random import randint, choice


class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game_widget = BreakoutGame(self)
        self.add_widget(self.game_widget)

        # UI elements with dynamic positioning
        self.score_label = Label(
            text="Score: 0",
            size_hint=(None, None), size=(150, 30),
            pos_hint={"left": 1, "top": 1}
        )
        self.lives_label = Label(
            text="Lives: 3",
            size_hint=(None, None), size=(150, 30),
            pos_hint={"center_x": 0.5, "top": 1}
        )
        self.back_button = Button(
            text="Back to Menu",
            size_hint=(None, None), size=(150, 50),
            pos_hint={"right": 1, "top": 1}
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
        padding = 10  # ระยะขอบ
        self.score_label.pos = (padding, height - 40)
        self.lives_label.pos = (width / 2 - 75, height - 40)
        self.back_button.pos = (width - 160, height - 50)

    def back_to_menu(self, instance):
        self.manager.current = "menu"


class BreakoutGame(Widget):
    def __init__(self, game_screen, **kwargs):
        super().__init__(**kwargs)
        self.game_screen = game_screen
        self.ball = None
        self.paddle = None
        self.blocks = []
        self.dx = 2
        self.dy = 2
        self.lives = 3
        self.score = 0
        self.running = False
        self.moving_left = False
        self.moving_right = False
        self.level = 1  # เริ่มที่ Level 1
        self.paddle_speed = 12  # ปรับค่า speed ตามต้องการ
        self.setup_game()

        Window.bind(on_resize=self.update_game_elements)
        Window.bind(on_key_down=self.on_key_down)
        Window.bind(on_key_up=self.on_key_up)

    def setup_game(self):
        self.canvas.clear()
        difficulty = get_difficulty()
    
        # ดึงค่าความยากของโหมดที่เลือก
        settings = {
        "easy": {"speed": 2, "paddle_size": 150, "lives": 4},
        "medium": {"speed": 3, "paddle_size": 120, "lives": 3},
        "hard": {"speed": 4, "paddle_size": 100, "lives": 2},
        }[difficulty]

        # เพิ่มระดับความเร็วและปรับแต่งตาม Level
        self.dx = settings["speed"] 
        self.dy = settings["speed"] 
        self.lives = settings["lives"]

        with self.canvas:
            Color(0, 0, 0)
            Rectangle(size=Window.size)

            # สร้างเส้นแยก UI
            Color(1, 1, 1)
            Line(points=[0, Window.height - 60, Window.width, Window.height - 60], width=2)

            # สร้าง Paddle
            Color(1, 1, 1)
            self.paddle = Rectangle(size=(settings["paddle_size"], 20), pos=(Window.width / 2 - settings["paddle_size"] / 2, 50))

            # สร้าง Ball
            Color(1, 1, 1)
            self.ball = Ellipse(size=(20, 20), pos=(Window.width / 2, Window.height / 2))

            # สร้างบล็อกโดยใช้ setup_level()
            self.blocks = []
            self.setup_level()


            self.running = True

    def setup_level(self):
        self.blocks = []
        block_color = (1, 0, 0)  # สีแดง (สามารถเปลี่ยนเป็นสีอื่นได้ตามต้องการ)
        
        if self.level == 1:  # Level 1: 2 columns x 2 rows
            cols = 2
            rows = 2

        elif self.level == 2: # Level 2: 3 columns x 3 rows
            cols = 3
            rows = 3

        elif self.level == 3:  # Level 3: 4 columns x 4 rows
            cols = 4
            rows = 4

        block_width = Window.width / cols
        block_height = 30
        block_start_y = Window.height - 90

        for row in range(rows):
         for col in range(cols):
            with self.canvas:
                Color(*block_color)
                block = Rectangle(
                    size=(block_width - 5, block_height - 5),
                    pos=(col * block_width, block_start_y - (row * block_height))
                )
                self.blocks.append(block)

    def update_game_elements(self, instance, width, height):
        # Update paddle position to be centered
        paddle_size = self.paddle.size[0]  # Keep original paddle size
        self.paddle.pos = (width / 2 - paddle_size / 2, self.paddle.pos[1])
        
        if self.level == 1:
            cols = 2
            rows = 2

        elif self.level == 2:
            cols = 3
            rows = 3

        elif self.level == 3:
            cols = 4
            rows = 4

        # Adjust block grid based on the new window size
       
        block_width = width / cols  # Adjust based on number of columns
        block_height = 30
        block_start_y = height - 90

        index = 0
        for row in range(rows):
            for col in range(cols):
                if index < len(self.blocks):
                    self.blocks[index].pos = (col * block_width, block_start_y - (row * block_height))
                    index += 1

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

        if self.ball.pos[1] <= self.paddle.pos[1] + self.paddle.size[1] and self.paddle.pos[0] <= self.ball.pos[0] <= self.paddle.pos[0] + self.paddle.size[0]:
            self.dy *= -1

        # ตรวจสอบการชนกับบล็อก
        for block in self.blocks[:]:
            if block.pos[0] <= self.ball.pos[0] <= block.pos[0] + block.size[0] and block.pos[1] <= self.ball.pos[1] <= block.pos[1] + block.size[1]:
                self.blocks.remove(block)
                self.canvas.remove(block)
                self.dy *= -1
                self.score += 10
                self.game_screen.update_labels()

        # ถ้าทำลายบล็อกทั้งหมด เปลี่ยนด่าน
        if not self.blocks:
            self.next_level()

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
        
    def next_level(self):
        self.level += 1  # เพิ่มระดับ
        if self.level > 3:  # จำกัดไว้ที่ 3 ด่าน
            self.running = False
            Clock.unschedule(self.update)
            self.show_game_over_message()
            return

        # เพิ่มความเร็วของลูกบอลทีละน้อย แต่ไม่ให้เร็วเกินไป
        self.dx *= 1.1
        self.dy *= 1.1
        self.setup_game()  # รีเซ็ตเกมใหม่
        self.start_game()  # เริ่มเกมใหม่


    def on_touch_move(self, touch):
        new_x = touch.x - self.paddle.size[0] / 2
        new_x = max(0, min(Window.width - self.paddle.size[0], new_x))
        self.paddle.pos = (new_x, self.paddle.pos[1])


    def on_key_down(self, window, key, scancode, codepoint, modifier):
        if codepoint == "a":
            self.moving_left = True
        elif codepoint == "d":
            self.moving_right = True

        # เริ่มเลื่อน paddle
        Clock.unschedule(self.move_paddle)  # ป้องกันการเรียกซ้ำ
        Clock.schedule_interval(self.move_paddle, 1 / 60)

    def on_key_up(self, window, key, scancode):
        if key in (ord("a"), ord("d")):  
            self.moving_left = False
            self.moving_right = False

        # หยุดการเลื่อน paddle ถ้าไม่ได้กดปุ่มใดอยู่
        if not self.moving_left and not self.moving_right:
            Clock.unschedule(self.move_paddle)

    def move_paddle(self, dt):
        if self.moving_left:
            new_x = max(self.paddle.pos[0] - self.paddle_speed, 0)
            self.paddle.pos = (new_x, self.paddle.pos[1])
        if self.moving_right:
            new_x = min(self.paddle.pos[0] + self.paddle_speed, Window.width - self.paddle.size[0])
            self.paddle.pos = (new_x, self.paddle.pos[1])