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
        self.root.geometry("1280x720")  # Adjust to match your background image size
        self.root.resizable(False, False)  # Prevent window resizing
        
        self.top_level = load_top_level()
        self.setup_ui()
        self.root.bind('<Escape>', self.quit_game)
        
        if music_on:
            background_music.play(-1)

    def setup_ui(self):
        self.bg_image = tk.PhotoImage(file="image.png")
        self.bg_label = tk.Label(self.root, image=self.bg_image)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Adjust button positions using relx and rely
        start_button = tk.Button(self.root, text="Start", font=("ROG Fonts", 18), width=10, command=self.start_game)
        start_button.place(relx=0.5, rely=0.4, anchor='center')
        
        quit_button = tk.Button(self.root, text="Quit", font=("ROG Fonts", 18), width=10, command=self.quit_game)
        quit_button.place(relx=0.5, rely=0.5, anchor='center')
        
        self.setup_sound_button()
        
        # Adjust label positions
        self.total_score_label = tk.Label(self.root, text=f"Total Score: {total_score}", font=("ROG Fonts", 14))
        self.total_score_label.place(relx=0.5, rely=0.6, anchor='center')
        
        self.top_level_label = tk.Label(self.root, text=f"Top Level: {self.top_level}", font=("ROG Fonts", 14))
        self.top_level_label.place(relx=0.5, rely=0.67, anchor='center')
        
    def quit_game(self, event=None):
        background_music.stop()
        self.root.destroy()  

    def setup_sound_button(self):
        self.sound_on_image = tk.PhotoImage(file="opensound.png").subsample(35)
        self.sound_off_image = tk.PhotoImage(file="closesound.png").subsample(18)
        
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
        self.root.geometry("1280x720")  # Adjust to match your background image size
        self.root.resizable(False, False)  # Prevent window resizing
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
        
        self.question_label = tk.Label(self.root, text="", font=("Fixedsys", 26, "bold"), bg='SystemButtonFace')
        self.question_label.place(relx=0.5, rely=0.2, anchor='center')
        
        self.timer_label = tk.Label(self.root, text=f"เวลา: {self.time_left:02d}", font=("Algerian", 18), bg='SystemButtonFace')
        self.timer_label.place(relx=0.5, rely=0.3, anchor='center')
        
        self.choice_frame = tk.Frame(self.root, bg='SystemButtonFace')
        self.choice_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        self.choice_buttons = []
        for i in range(4):
            btn = tk.Button(self.choice_frame, text="", font=("ROG Fonts", 14), width=20, height=2,
                            command=lambda idx=i: self.check_answer(idx))
            btn.grid(row=i // 2, column=i % 2, padx=10, pady=10)
            self.choice_buttons.append(btn)
        
        self.score_label = tk.Label(self.root, text=f"คะแนน: {self.score}", font=("Arial", 18), bg='SystemButtonFace')
        self.score_label.place(relx=0.2, rely=0.9, anchor='center')
        
        self.level_label = tk.Label(self.root, text=f"เลเวล: {self.level}", font=("Arial", 18), bg='SystemButtonFace')
        self.level_label.place(relx=0.8, rely=0.9, anchor='center')
        
        self.streak_frame = tk.Frame(self.root, bg='SystemButtonFace')
        self.streak_frame.place(relx=0.5, rely=0.8, anchor='center')
        
        self.streak_boxes = []
        for i in range(10):
            box = tk.Label(self.streak_frame, text=str(i + 1), font=("Arial", 14), width=5, height=2, relief="raised", bg="gray")
            box.pack(side='left', padx=2)
            self.streak_boxes.append(box)
        
        self.setup_sound_button()
    def setup_sound_button(self):
        self.sound_on_image = tk.PhotoImage(file="opensound.png").subsample(35)
        self.sound_off_image = tk.PhotoImage(file="closesound.png").subsample(18)
        self.exit_image = tk.PhotoImage(file="exit.png").subsample(27)
        
        self.sound_button = tk.Button(self.root, image=self.sound_on_image, command=self.toggle_sound)
        self.sound_button.place(x=10, y=10)
        self.exit_button = tk.Button(self.root, image=self.exit_image, command=self.quit_game)
        self.exit_button.place(x=1460, y=10)

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
            self.score_label.config(text=f"คะแนน: {self.score}")
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
            self.streak_boxes[self.streak_count - 1].config(bg="green")
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
            self.time_left = 60  # Reset time to 60 seconds
            if sound_on:
                level_up_sound.play()
            messagebox.showinfo("Level Up!", f"ยินดีด้วย! คุณผ่านไปยังเลเวล {self.level}")
            self.level_label.config(text=f"เลเวล: {self.level}")
            self.question_count = 0
            self.streak_count = 0
            for box in self.streak_boxes:
                box.config(bg="gray")
                 
            # Update background image for the new level
            self.bg_image = tk.PhotoImage(file=self.level_backgrounds[self.level])
            self.bg_label.config(image=self.bg_image)
            self.new_question()
        else:
            self.complete_game()

    def complete_game(self):
        messagebox.showinfo("ยินดีด้วย!", f"คุณเก่งมาก ทำสถิติ 10 เลเวล\nจำนวนข้อที่ทำได้: {self.current_streak}")
        self.end_game()

    def update_timer(self):
        if self.game_running and self.time_left > 0:
            self.time_left -= 1
            if hasattr(self, 'timer_label') and self.timer_label.winfo_exists():
                self.timer_label.config(text=f"เวลา: {self.time_left:02d}")
                self.root.after(1000, self.update_timer)
            else:
                self.game_running = False
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
        self.root.geometry("1912x985")  # Adjust to match your background image size
        self.root.resizable(False, False)  # Prevent window resizing
        
        self.level = level
        self.score = score
        self.top_level = top_level
        self.setup_ui()
        self.root.bind('<Escape>', self.quit_game)

    def setup_ui(self):
        self.bg_image = tk.PhotoImage(file="bg10.png")
        self.bg_label = tk.Label(self.root, image=self.bg_image)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        
        game_over_label = tk.Label(self.root, text="Game Over", font=("ROG Fonts", 24, "bold"), bg='SystemButtonFace')
        game_over_label.place(relx=0.5, rely=0.3, anchor='center')
        
        level_label = tk.Label(self.root, text=f"Highest Level Reached: {self.level}", font=("ROG Fonts", 18), bg='SystemButtonFace')
        level_label.place(relx=0.5, rely=0.4, anchor='center')
        
        score_label = tk.Label(self.root, text=f"Your Score: {self.score}", font=("ROG Fonts", 18), bg='SystemButtonFace')
        score_label.place(relx=0.5, rely=0.5, anchor='center')
        
        main_menu_button = tk.Button(self.root, text="Main Menu", font=("ROG Fonts", 18), width=20, command=self.return_to_main_menu)
        main_menu_button.place(relx=0.5, rely=0.6, anchor='center')


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
        if self.level <= 3:
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
        
        num1 = random.randint(1, 10 * self.level)
        num2 = random.randint(1, 10 * self.level)
        if op_symbol == "-":
            num1, num2 = max(num1, num2), min(num1, num2)
        question = f"{num1} {op_symbol} {num2}"
        answer = operation(num1, num2)
        
        choices = [answer]
        while len(choices) < 4:
            fake_answer = random.randint(max(0, answer - 10), answer + 10)
            if fake_answer != answer and fake_answer not in choices:
                choices.append(fake_answer)
        random.shuffle(choices)
        
        return question, answer, choices

    def generate_intermediate_question(self):
        operations = ["*", "/", "√", "log"]
        op_symbol = random.choice(operations)
        
        if op_symbol == "*":
            num1 = random.randint(2, 12)
            num2 = random.randint(2, 12)
            question = f"{num1} × {num2}"
            answer = num1 * num2
        elif op_symbol == "/":
            answer = random.randint(1, 10)
            num2 = random.randint(2, 10)
            num1 = answer * num2
            question = f"{num1} ÷ {num2}"
        elif op_symbol == "√":
            num = random.randint(1, 100)
            question = f"√{num}"
            answer = round(math.sqrt(num), 2)
        else:  # log
            base = random.choice([2, 10])
            num = random.randint(2, 100)
            question = f"log{base}({num})"
            answer = round(math.log(num, base), 2)
        
        choices = [answer]
        while len(choices) < 4:
            fake_answer = round(random.uniform(answer * 0.5, answer * 1.5), 2)
            if fake_answer != answer and fake_answer not in choices:
                choices.append(fake_answer)
        random.shuffle(choices)
        
        return question, answer, choices

    def generate_advanced_question(self):
        functions = ["sin", "cos", "tan", "PI"]
        func = random.choice(functions)
        
        if func in ["sin", "cos", "tan"]:
            angle = random.choice([0, 30, 45, 60, 90, 180, 270, 360])
            question = f"{func}({angle}°)"
            if func == "sin":
                answer = round(math.sin(math.radians(angle)), 2)
            elif func == "cos":
                answer = round(math.cos(math.radians(angle)), 2)
            else:  # tan
                if angle not in [90, 270]:
                    answer = round(math.tan(math.radians(angle)), 2)
                else:
                    return self.generate_advanced_question()  # Regenerate if tan(90) or tan(270)
        else:  # PI
            operation = random.choice(["+", "-", "*", "/"])
            num = random.randint(1, 5)
            question = f"π {operation} {num}"
            if operation == "+":
                answer = round(math.pi + num, 2)
            elif operation == "-":
                answer = round(math.pi - num, 2)
            elif operation == "*":
                answer = round(math.pi * num, 2)
            else:
                answer = round(math.pi / num, 2)
        
        choices = [answer]
        while len(choices) < 4:
            fake_answer = round(random.uniform(answer - 1, answer + 1), 2)
            if fake_answer != answer and fake_answer not in choices:
                choices.append(fake_answer)
        random.shuffle(choices)
        
        return question, answer, choices

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

