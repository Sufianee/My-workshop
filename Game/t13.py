import tkinter as tk
from tkinter import messagebox
import random
import operator
import os
import math
import pygame

pygame.init()
pygame.mixer.init()

# Load sounds
correct_sound = pygame.mixer.Sound("Yes.mp3")
incorrect_sound = pygame.mixer.Sound("No.mp3")
level_up_sound = pygame.mixer.Sound("ifelse.mp3")
background_music = pygame.mixer.Sound("play_bg.mp3")

sound_on = True
music_on = True
background_music.play(-1)

def load_total_score():
    if os.path.exists("total_score.txt"):
        with open("total_score.txt", "r") as file:
            return int(file.read().strip())
    return 0

def save_total_score(score):
    with open("total_score.txt", "w") as file:
        file.write(str(score))

total_score = load_total_score()

def load_top_level():
    if os.path.exists("top_level.txt"):
        with open("top_level.txt", "r") as file:
            return min(int(file.read().strip()), 10)
    return 1  # Default to 1 if no file exists

def save_top_level(level):
    with open("top_level.txt", "w") as file:
        file.write(str(min(level, 10)))

class MainMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("SMART KID")
        self.root.geometry("1280x720")
        self.root.resizable(False, False)
        
        self.top_level = load_top_level()
        self.setup_ui()
        self.root.bind('<Escape>', self.quit_game)
        if music_on:
            background_music.play(-1)
        
    def setup_ui(self):
        self.bg_image = tk.PhotoImage(file="bgmain.png")
        self.bg_label = tk.Label(self.root, image=self.bg_image)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        
        start_button = tk.Button(self.root, text="Start", font=("ROG Fonts", 22), width=10, command=self.start_game)
        start_button.place(relx=0.5, rely=0.20, anchor='center')
        quit_button = tk.Button(self.root, text="Quit", font=("ROG Fonts", 22), width=10, command=self.quit_game)
        quit_button.place(relx=0.5, rely=0.30, anchor='center') 
        self.setup_sound_button()
        
        self.total_score_label = tk.Label(self.root, text=f"Total Score : {total_score}",font=("Comic Sans MS", 20), bg='pink', fg='black')
        self.total_score_label.place(relx=0.5, rely=0.42, anchor='center')
        self.top_level_label = tk.Label(self.root, text=f"Top Level : {self.top_level}", font=("Comic Sans MS", 20), bg='lightblue', fg='black')
        self.top_level_label.place(relx=0.5, rely=0.52, anchor='center')

    def quit_game(self, event=None):
        background_music.stop()
        self.root.destroy()  

    def setup_sound_button(self):
        self.sound_on_image = tk.PhotoImage(file="opensound.png").subsample(35)
        self.sound_off_image = tk.PhotoImage(file="closesound.png").subsample(35)
        
        self.sound_button = tk.Button(self.root, image=self.sound_on_image, command=self.toggle_sound)
        self.sound_button.place(x=10, y=10)

    def toggle_sound(self):
        global sound_on, music_on    
        sound_on = not sound_on
        music_on = not music_on
        if sound_on and music_on:
            self.sound_button.config(image=self.sound_on_image)
            pygame.mixer.unpause()
            background_music.play(-1)
        else:
            self.sound_button.config(image=self.sound_off_image)
            pygame.mixer.pause()
            background_music.stop()

    def start_game(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        game = MathQuizGame(self.root)

class MathQuizGame:
    def __init__(self, root):
        self.root = root
        self.root.title("SMART KID")
        self.root.geometry("1280x720")
        self.root.resizable(False, False)
        self.level = 1
        self.time_left = 60
        self.score = 0
        self.question_count = 0
        self.current_streak = 0
        self.quiz_generator = MathQuizGenerator(self.level)
        self.streak_count = 0
        self.top_level = load_top_level()
        self.game_running = True
        self.level_backgrounds = {
            1: "bg1.png", 2: "bg2.png", 3: "bg3.png", 4: "bg4.png", 5: "bg5.png",
            6: "bg6.png", 7: "bg7.png", 8: "bg8.png", 9: "bg9.png", 10: "bg10.png"
        }
        self.setup_ui()
        self.new_question()
        self.update_timer()
        self.root.bind('<Escape>', self.quit_game)
        if music_on:
            background_music.play(-1)

    def setup_ui(self):
        self.bg_image = tk.PhotoImage(file=self.level_backgrounds[self.level])
        self.bg_label = tk.Label(self.root, image=self.bg_image)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        
        self.question_label = tk.Label(self.root, text="", font=("Comic Sans MS", 26, "bold"))
        self.question_label.pack(pady=10)
        self.timer_label = tk.Label(self.root, text=f"Time: {self.time_left:02d}", 
                                    font=("Comic Sans MS", 18), bg='white', fg='black')
        self.timer_label.pack(pady=5)
        
        self.choice_frame = tk.Frame(self.root)
        self.choice_frame.pack()
        
        self.choice_buttons = []
        for i in range(4):
            btn = tk.Button(self.choice_frame, text="", font=("ROG Fonts", 14), width=20, height=2,
                            command=lambda idx=i: self.check_answer(idx))
            btn.grid(row=i // 2, column=i % 2, padx=10, pady=10)
            self.choice_buttons.append(btn)
        self.score_label = tk.Label(self.root, text=f"Score: {self.score}", font=("Comic Sans MS", 20), bg='yellow', fg='black')
        self.score_label.pack(pady=20)
        self.level_label = tk.Label(self.root, text=f"Level: {self.level}", font=("Comic Sans MS", 20), bg='pink', fg='black')
        self.level_label.pack(pady=20)
        self.streak_frame = tk.Frame(self.root)
        self.streak_frame.pack(pady=10)
        self.streak_boxes = []
        for i in range(10):
            box = tk.Label(self.streak_frame, text=str(i + 1), font=("Arial", 14), width=5, height=2, relief="raised", bg="gray")
            box.pack(side='left', padx=2)
            self.streak_boxes.append(box)
        self.setup_sound_button()

    def setup_sound_button(self):
        self.sound_on_image = tk.PhotoImage(file="opensound.png").subsample(35)
        self.sound_off_image = tk.PhotoImage(file="closesound.png").subsample(35)
        self.exit_image = tk.PhotoImage(file="exit.png").subsample(35)
        
        self.sound_button = tk.Button(self.root, image=self.sound_on_image, command=self.toggle_sound)
        self.sound_button.place(x=10, y=10)
        self.exit_button = tk.Button(self.root, image=self.exit_image, command=self.quit_game)
        self.exit_button.place(x=1190, y=10)

    def toggle_sound(self):
        global sound_on
        sound_on = not sound_on
        if sound_on:
            self.sound_button.config(image=self.sound_on_image)
            pygame.mixer.unpause()
        else:
            self.sound_button.config(image=self.sound_off_image)
            pygame.mixer.pause()

    def generate_math_question(self):
        return self.quiz_generator.generate_math_question()

    def new_question(self):
        if not self.game_running:
            return
        if self.level == 10 and self.question_count >= 10:
            self.complete_game()
        elif self.question_count >= 10:
            self.level_up()
        else:
            self.quiz_generator.level = self.level
            self.current_question, self.current_answer, self.current_choices = self.generate_math_question()
            self.question_label.config(text=self.current_question)
            for i, choice in enumerate(self.current_choices):
                self.choice_buttons[i].config(text=str(choice), bg="lightblue", state="normal")
            self.question_count += 1    

    def check_answer(self, idx):
        if not self.game_running:
            return
        global total_score
        if idx == -1:  # หมดเวลา
            self.end_game()
            return
        selected_answer = self.current_choices[idx]
        if selected_answer == self.current_answer:
            self.score += 10
            total_score += 10
            save_total_score(total_score)
            self.score_label.config(text=f"Score: {self.score}")
            self.advance_streak()
            self.choice_buttons[idx].config(bg="lightgreen")
            if sound_on:
                correct_sound.play()
            self.root.after(500, self.new_question)
        else:
            if sound_on:
                incorrect_sound.play()
            for btn in self.choice_buttons:
                btn.config(bg="lightcoral", state="disabled")
            correct_idx = self.current_choices.index(self.current_answer)
            self.choice_buttons[correct_idx].config(bg="lightgreen")
            if total_score >= 500:
                response = messagebox.askyesno("แลกคะแนน", "คุณต้องการแลก 500 คะแนนจากคะแนนรวม เพื่อจะเล่นต่อหรือไม่?")
                if response:
                    total_score -= 500
                    save_total_score(total_score)
                    self.root.after(500, self.reset_current_question)
                else:
                    self.end_game()
            else:
                self.end_game()

    def reset_current_question(self):
        if not self.game_running:
            return
        self.current_question, self.current_answer, self.current_choices = self.generate_math_question()
        self.question_label.config(text=self.current_question)
        for i, choice in enumerate(self.current_choices):
            self.choice_buttons[i].config(text=str(choice), bg="lightblue", state="normal")

    def advance_streak(self):
        self.current_streak += 1
        self.streak_count += 1
        if self.streak_count <= 10:
            self.streak_boxes[self.streak_count - 1].config(bg="lightgreen")
        if self.streak_count == 10:
            self.streak_count = 0
            for box in self.streak_boxes:
                box.config(bg="gray")

    def reset_streak(self):
        self.current_streak = 0
        for box in self.streak_boxes:
            box.config(bg="gray")

    def level_up(self):
        if not self.game_running:
            return
        if self.level < 10:
            self.level += 1
            self.time_left = 60  # Reset time to
    def level_up(self):
        if not self.game_running:
            return
        if self.level < 10:
            self.level += 1
            self.time_left = 60  # Reset time to 60 seconds
            if sound_on:
                level_up_sound.play()
            
            # สร้างหน้าต่างใหม่สำหรับแสดงผลการชนะ
            win_window = tk.Toplevel(self.root)
            win_window.title("You Win!")
            win_window.geometry("400x300")
            win_window.resizable(False, False)
            # สร้าง Canvas สำหรับวาดพื้นหลังและปุ่ม
            canvas = tk.Canvas(win_window, width=400, height=300, bg="black")
            canvas.pack()
            # วาดกรอบสีขาว
            canvas.create_rectangle(20, 20, 380, 280, outline="white", width=5)
            # แสดงข้อความ
            if self.level == 10:
                canvas.create_text(200, 60, text="CONGRATULATIONS!", fill="white", font=("Arial", 20, "bold"))
            else:
                canvas.create_text(200, 60, text="YOU WIN!", fill="white", font=("Arial", 20, "bold"))
            canvas.create_text(200, 100, text=f"Score: {self.score}", fill="white", font=("Arial", 16))
            canvas.create_text(200, 140, text=f"High Score: {total_score}", fill="white", font=("Arial", 16))
            # สร้างปุ่ม Home
            home_button = tk.Button(win_window, text="Home", command=lambda: self.return_to_main_menu(win_window))
            home_button.place(x=100, y=200, width=100, height=40)
            # สร้างปุ่ม Next Level ถ้ายังไม่ถึงเลเวลสุดท้าย
            if self.level < 10:
                next_button = tk.Button(win_window, text="Next Level", command=lambda: self.start_next_level(win_window))
                next_button.place(x=220, y=200, width=100, height=40)
        else:
            self.complete_game()

    def return_to_main_menu(self, win_window):
        win_window.destroy()
        self.end_game()

    def start_next_level(self, win_window):
        win_window.destroy()
        self.question_count = 0
        self.streak_count = 0
        for box in self.streak_boxes:
            box.config(bg="gray")
        
        # อัพเดทภาพพื้นหลังสำหรับเลเวลใหม่
        self.bg_image = tk.PhotoImage(file=self.level_backgrounds[self.level])
        self.bg_label.config(image=self.bg_image)
        
        self.level_label.config(text=f"เลเวล: {self.level}")
        self.new_question()

    def complete_game(self):
        messagebox.showinfo("ยินดีด้วย!", f"คุณเก่งมาก ทำสถิติ 10 เลเวล\nจำนวนข้อที่ทำได้: {self.current_streak}")
        self.end_game()

    def update_timer(self):
        if self.game_running and self.time_left > 0:
            self.time_left -= 1
            self.timer_label.config(text=f"Time: {self.time_left:02d}")
            self.root.after(1000, self.update_timer)
        elif self.game_running:
            self.check_answer(-1)  # Call check_answer with -1 to handle timeout

    def end_game(self):
        self.game_running = False
        background_music.stop()
        save_last_score(self.score)
        if self.level == 10:
            self.top_level = 10
        elif self.level > self.top_level:
            self.top_level = self.level
        save_top_level(self.top_level)
        for widget in self.root.winfo_children():
            widget.destroy()
        EndScreen(self.root, self.level, self.score, self.top_level)

    def quit_game(self, event=None):
        self.game_running = False
        background_music.stop()
        self.root.destroy()

class EndScreen:
     def __init__(self, root, level, score, top_level):
        self.root = root
        self.root.title("Game Over")
        self.root.geometry("1280x720")  # Adjust to match your background image size
        self.root.resizable(False, False)  # Prevent window resizing
        
        self.level = level
        self.score = score
        self.top_level = top_level
        self.setup_ui()
        self.root.bind('<Escape>', self.quit_game)

     def quit_game(self, event=None):
        background_music.stop()
        self.root.destroy()

     def setup_ui(self):
        self.bg_image = tk.PhotoImage(file="bbgend.png")
        self.bg_label = tk.Label(self.root, image=self.bg_image)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        level_label = tk.Label(self.root, text=f"Highest Level : {self.level}",  font=("Comic Sans MS", 20), bg='orange', fg='black')
        level_label.place(relx=0.5, rely=0.25, anchor='center')
        score_label = tk.Label(self.root, text=f"Your Score: {self.score}",  font=("Comic Sans MS", 20), bg='yellow', fg='black')
        score_label.pack(pady=220)
        main_menu_button = tk.Button(self.root, text="Main Menu", font=("ROG Fonts", 18), width=10, command=self.return_to_main_menu)
        main_menu_button.place(relx=0.5, rely=0.42, anchor='center')

     def return_to_main_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        if music_on:
            background_music.play(-1)
        MainMenu(self.root)

class MathQuizGenerator:
    def __init__(self, level):
        self.level = level

    def generate_math_question(self):
        if 1 <= self.level <= 3:
            return self.generate_basic_question()
        elif 4 <= self.level <= 6:
            return self.generate_intermediate_question()
        else:
            return self.generate_advanced_question()

    def generate_basic_question(self):
        operations = {
            "+": operator.add,
            "-": operator.sub,
            "*": operator.mul
        }
        
        op_symbol, operation = random.choice(list(operations.items()))
        
        num1 = random.randint(-10, 10 * self.level)
        num2 = random.randint(1, 10 * self.level)
        
        question = f"{num1} {op_symbol} {num2}"
        answer = operation(num1, num2)
        
        choices = self.generate_choices(answer)
        
        return question, answer, choices

    def generate_intermediate_question(self):
        operation = random.choice(["/", "mod", "root", "power"])
        
        if operation == "/":
            num2 = random.randint(1, 10)
            num1 = num2 * random.randint(1, 10)
            question = f"{num1} / {num2}"
            answer = num1 // num2
        elif operation == "mod":
            num2 = random.randint(2, 10)
            num1 = random.randint(1, 50)
            question = f"{num1} mod {num2}"
            answer = num1 % num2
        elif operation == "root":
            answer = random.randint(2, 20)
            num = answer ** 2
            question = f"√{num}"
        else:  # power
            base = random.randint(-20, 20)
            exponent = random.randint(2, 4)
            question = f"{base}^{exponent}"
            answer = base ** exponent
        
        choices = self.generate_choices(answer)
        
        return question, answer, choices

    def generate_advanced_question(self):
        operation = random.choice(["sin", "cos", "tan", "log"])
        
        if operation in ["sin", "cos", "tan"]:
            angle = random.choice([0, 30, 45, 60, 90])
            question = f"{operation}({angle}°)"
            if operation == "sin":
                answer = round(math.sin(math.radians(angle)), 2)
            elif operation == "cos":
                answer = round(math.cos(math.radians(angle)), 2)
            else:
                if angle != 90:
                    answer = round(math.tan(math.radians(angle)), 2)
                else:
                    return self.generate_advanced_question()  # Regenerate if tan(90°)
        else:  # log
            base = random.choice([2, 10])
            if base == 2:
                num = 2 ** random.randint(1, 5)
            else:
                num = 10 ** random.randint(1, 3)
            question = f"log{base}({num})"
            answer = int(math.log(num, base))
        
        choices = self.generate_choices(answer, is_trigonometric=(operation in ["sin", "cos", "tan"]))
        
        return question, answer, choices

    def generate_choices(self, answer, is_trigonometric=False):
        choices = [answer]
        if is_trigonometric:
            # สำหรับฟังก์ชันตรีโกณมิติ สร้างตัวเลือกที่เป็นทศนิยม 2 ตำแหน่ง
            while len(choices) < 4:
                fake_answer = round(random.uniform(-1, 1), 2)
                if abs(fake_answer - answer) > 0.05 and fake_answer not in choices:
                    choices.append(fake_answer)
        else:
            # สำหรับฟังก์ชันอื่นๆ ที่ให้คำตอบเป็นจำนวนเต็ม
            while len(choices) < 4:
                fake_answer = random.randint(int(answer) - 10, int(answer) + 10)
                if fake_answer != answer and fake_answer not in choices:
                    choices.append(fake_answer)
        
        random.shuffle(choices)
        return choices

def save_last_score(score):
    with open("score.txt", "w") as file:
        file.write(str(score))

def load_last_score():
    if os.path.exists("score.txt"):
        with open("score.txt", "r") as file:
            return int(file.read().strip())
    return 0  # Default to 0 if no file exists

if __name__ == "__main__":
    root = tk.Tk()
    
    def quit_game(event=None):
        background_music.stop()
        root.destroy()
    
    root.bind('<Escape>', quit_game)
    
    top_level = load_top_level()
    MainMenu(root)
    root.mainloop()                                                                                                                                  
