from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Rectangle, Ellipse, Color, Line
from kivy.clock import Clock
from kivy.core.window import Window
from utils.config import get_difficulty
from random import randint, choice
from kivy.core.audio import SoundLoader
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image

class PowerUp:
    def __init__(self, x, y, effect):
        self.effect = effect  # พลังพิเศษ (ขยายแพดเดิล, เพิ่มลูกบอล, เพิ่มความเร็ว)
        self.image = Image(source="assets/image/powerups.jpg", size=(30, 30), pos=(x, y))
        self.falling_speed = 1  # ความเร็วตก

    def move_down(self):
        self.image.pos = (self.image.pos[0], self.image.pos[1] - self.falling_speed)
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
        self.dx = 0.5
        self.dy = 0.5
        self.lives = 3
        self.score = 0
        self.running = False
        self.paused = False  # ✅ เพิ่มตัวแปร paused ที่นี่
        self.moving_left = False
        self.moving_right = False
        self.level = 1  # เริ่มที่ Level 1
        self.paddle_speed = 12  # ปรับค่า speed ตามต้องการ
        self.powerups = []  # เก็บไอเทมที่กำลังตกลงมา
        self.extra_balls = []  # 🏀 เพิ่มตัวแปรสำหรับเก็บลูกบอลเสริม
        self.setup_game()

        # โหลดไฟล์เสียง
        self.hit_sound = SoundLoader.load('assets/sounds/hit.wav')  # เสียงเมื่อชนบล็อก
        self.break_sound = SoundLoader.load('assets/sounds/break.wav')  # เสียงเมื่อบล็อกถูกทำลาย

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
        block_color = (1, 0, 0, 1)  # สีแดง (RGBA)
        
        if self.level == 1:  # Level 1: 2 columns x 2 rows
            cols = 7
            rows = 2
        elif self.level == 2:  # Level 2: 3 columns x 3 rows
            cols = 7
            rows = 3
        elif self.level == 3:  # Level 3: 4 columns x 4 rows
            cols = 7
            rows = 4

        block_width = Window.width / cols
        block_height = 30
        block_start_y = Window.height - 90

        for row in range(rows):
            # กำหนด hit_points โดยแถวบนสุด (row 0) มี 3 HP และลดลงตามลำดับ
            hit_points = max(1, 3 - row)  # เริ่มที่ 3 และลดลง 1 ต่อแถว แต่ไม่ต่ำกว่า 1
            for col in range(cols):
                with self.canvas:
                    color = Color(*block_color)  # สร้าง Color object
                    block = Rectangle(
                        size=(block_width - 5, block_height - 5),
                        pos=(col * block_width, block_start_y - (row * block_height))
                    )
                    block_data = {
                        "rectangle": block,
                        "hit_points": hit_points,  # กำหนดพลังชีวิตตามแถว
                        "color": color             # เก็บ Color object
                    }
                    self.blocks.append(block_data)
                    self.update_block_color(block_data)  # อัปเดตสีตาม hit_points

    def update_block_color(self, block):
        hit_points = block["hit_points"]
        color = block["color"]  # ใช้ Color object ที่เก็บไว้
        # อัปเดตสีตาม hit_points
        if hit_points == 3:
            color.rgba = (1, 0, 0, 1)  # สีแดง
        elif hit_points == 2:
            color.rgba = (0, 0, 1, 1)  # สีฟ้า
        else:  # hit_points == 1
            color.rgba = (1, 1, 0, 1)  # สีเหลือง

    def update_game_elements(self, instance, width, height):
        # Update paddle position to be centered
        paddle_size = self.paddle.size[0]  # Keep original paddle size
        self.paddle.pos = (width / 2 - paddle_size / 2, self.paddle.pos[1])
        
        if self.level == 1:
            cols = 7
            rows = 2
        elif self.level == 2:
            cols = 7
            rows = 3
        elif self.level == 3:
            cols = 7
            rows = 4
       
        block_width = width / cols  
        block_height = 30
        block_start_y = height - 90

        index = 0
        for row in range(rows):
            for col in range(cols):
                if index < len(self.blocks):
                    self.blocks[index]["rectangle"].pos = (col * block_width, block_start_y - (row * block_height))
                    index += 1

    def start_game(self):
        self.setup_game()
        Clock.schedule_interval(self.update, 1 / 60)
    
    def toggle_pause(self):
        self.paused = not self.paused  # สลับสถานะ Pause
        if self.paused:
            print("Game Paused")
            self.show_pause_popup()
        else:
            print("Game Resumed")
            if hasattr(self, "pause_popup"):
                self.pause_popup.dismiss()

    def show_pause_popup(self):
        layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        resume_button = Button(text="Resume", size_hint=(1, 0.5))
        exit_button = Button(text="Exit to Menu", size_hint=(1, 0.5))

        resume_button.bind(on_press=self.resume_game)
        exit_button.bind(on_press=self.exit_to_menu)

        layout.add_widget(resume_button)
        layout.add_widget(exit_button)

        self.pause_popup = Popup(
            title="Game Paused",
            content=layout,
            size_hint=(None, None),
            size=(300, 200),
            auto_dismiss=False
        )

        self.pause_popup.open()
        
    def resume_game(self, instance):
        self.toggle_pause()  # ปิด Pause และปิด Popup

    def exit_to_menu(self, instance):
        self.pause_popup.dismiss()
        self.running = False
        Clock.unschedule(self.update)
        self.game_screen.manager.current = "menu"

    def update(self, dt):
        if not self.running or self.paused:  # หยุดอัปเดตหาก paused
            return

        self.ball.pos = (self.ball.pos[0] + self.dx, self.ball.pos[1] + self.dy)

        if self.ball.pos[0] <= 0 or self.ball.pos[0] + self.ball.size[0] >= Window.width:
            self.dx *= -1

        if self.ball.pos[1] + self.ball.size[1] >= Window.height:
            self.dy *= -1

        if self.ball.pos[1] <= self.paddle.pos[1] + self.paddle.size[1] and self.paddle.pos[0] <= self.ball.pos[0] <= self.paddle.pos[0] + self.paddle.size[0]:
            self.dy *= -1
        
        for powerup in self.powerups[:]:  
            powerup.move_down()

                # เช็คว่าผู้เล่นรับไอเทมหรือยัง
            if self.paddle.pos[0] < powerup.image.pos[0] < self.paddle.pos[0] + self.paddle.size[0] and \
                self.paddle.pos[1] < powerup.image.pos[1] < self.paddle.pos[1] + self.paddle.size[1]:
                self.apply_powerup(powerup.effect)  # ใช้พลังพิเศษ
                self.remove_widget(powerup.image)
                self.powerups.remove(powerup)
                
         # อัปเดตบอลเสริมทั้งหมด
        for extra in self.extra_balls:
            extra["ball"].pos = (extra["ball"].pos[0] + extra["dx"], extra["ball"].pos[1] + extra["dy"])
            
        # ตรวจสอบการชนกับบล็อก
        for block in self.blocks[:]:
            block_rect = block["rectangle"]
            if block_rect.pos[0] <= self.ball.pos[0] <= block_rect.pos[0] + block_rect.size[0] and block_rect.pos[1] <= self.ball.pos[1] <= block_rect.pos[1] + block_rect.size[1]:
                block["hit_points"] -= 1  # ลดพลังชีวิต
                if block["hit_points"] <= 0:
                    if self.break_sound:
                        self.break_sound.play()  # เล่นเสียงเมื่อบล็อกถูกทำลาย
                    self.blocks.remove(block)
                    self.canvas.remove(block_rect)
                    self.score += 10
                    
                    # 🔥 สุ่มโอกาสดรอปไอเทม 30%
                    if randint(1, 100) <= 30:
                        powerup = PowerUp(block_rect.pos[0], block_rect.pos[1], choice(["expand_paddle", "extra_ball", "speed_up"]))
                        self.add_widget(powerup.image)
                        self.powerups.append(powerup)
                else:
                    if self.hit_sound:
                        self.hit_sound.play()
                    self.update_block_color(block)  # อัปเดตสีตาม hit_points
                self.dy *= -1
                self.game_screen.update_labels()
                break  # หยุดการตรวจสอบเมื่อชนบล็อกหนึ่งเพื่อป้องกันการชนซ้ำ

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
        self.dx *= 0.5
        self.dy *= 0.5
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
        elif codepoint == "p":  # กด 'P' เพื่อ Pause/Resume
            self.toggle_pause()

        Clock.unschedule(self.move_paddle)
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
            
    def apply_powerup(self, effect):
        if effect == "expand_paddle":
            self.paddle.size = (self.paddle.size[0] * 1.5, self.paddle.size[1])  # ขยาย Paddle
            self.paddle_color = Color(0, 1, 0, 1)  # เปลี่ยนเป็นสีเขียว
            self.canvas.add(self.paddle_color)
            self.canvas.add(self.paddle)
        elif effect == "extra_ball":
            self.create_extra_ball()
        elif effect == "speed_up":
            self.dx *= 0.2  # เพิ่มความเร็วลูกบอล
            self.dy *= 0.2  
    
    def create_extra_ball(self):
        new_ball = Ellipse(size=(20, 20), pos=self.ball.pos)
        self.canvas.add(Color(1, 1, 1))
        self.canvas.add(new_ball)
        self.extra_balls.append({"ball": new_ball, "dx": self.dx, "dy": self.dy})
