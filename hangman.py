import tkinter as tk
import random
import json
import os
import winsound

# ---------------- WORDS ----------------
words = ["python", "galaxy", "quantum", "rocket", "universe"]

score = 0
max_wrong = 6
current_player = ""
high_scores = {}

# ---------------- LOAD HIGHSCORES ----------------
if os.path.exists("highscores.json"):
    with open("highscores.json", "r") as f:
        high_scores = json.load(f)

# ---------------- WINDOW ----------------
root = tk.Tk()
root.title("🚀 Hangman ULTRA Arcade Edition")
root.geometry("850x720")
root.configure(bg="black")

# ---------------- STAR BACKGROUND ----------------
bg_canvas = tk.Canvas(root, width=850, height=720, bg="black", highlightthickness=0)
bg_canvas.place(x=0, y=0)

stars = []
for _ in range(100):
    x = random.randint(0, 850)
    y = random.randint(0, 720)
    star = bg_canvas.create_oval(x, y, x+2, y+2, fill="white", outline="")
    stars.append(star)

def animate_background():
    for star in stars:
        bg_canvas.move(star, 0, 2)
        x1,y1,x2,y2 = bg_canvas.coords(star)
        if y1 > 720:
            new_x = random.randint(0,850)
            bg_canvas.coords(star, new_x, 0, new_x+2, 2)
    root.after(50, animate_background)

animate_background()

# ---------------- LOGIN ----------------
login_frame = tk.Frame(root, bg="black")
login_frame.place(relx=0.5, rely=0.5, anchor="center")

tk.Label(login_frame, text="Enter Player Name",
         font=("Arial", 18, "bold"),
         bg="black", fg="#00ffcc").pack(pady=10)

name_entry = tk.Entry(login_frame, font=("Arial", 14))
name_entry.pack(pady=10)

def start_game():
    global current_player
    current_player = name_entry.get()
    if current_player == "":
        return
    login_frame.destroy()
    create_game_ui()
    new_game()

tk.Button(login_frame,
          text="Start Game",
          font=("Arial", 14, "bold"),
          bg="#00ffcc",
          command=start_game).pack(pady=10)

# ---------------- GAME UI ----------------
def create_game_ui():
    global word_label, score_label, attempts_label
    global result_label, buttons_frame, effect_canvas
    global highscore_label, restart_btn

    tk.Label(root, text="HANGMAN ULTRA",
             font=("Helvetica", 30, "bold"),
             bg="black", fg="#00ffcc").pack(pady=10)

    word_label = tk.Label(root, font=("Consolas", 32, "bold"),
                          bg="black", fg="white")
    word_label.pack(pady=20)

    score_label = tk.Label(root, font=("Arial", 14),
                           bg="black", fg="white")
    score_label.pack()

    highscore_label = tk.Label(root, font=("Arial", 14),
                               bg="black", fg="#00ffcc")
    highscore_label.pack()

    attempts_label = tk.Label(root, font=("Arial", 14),
                              bg="black", fg="red")
    attempts_label.pack()

    result_label = tk.Label(root, font=("Arial", 18, "bold"),
                            bg="black")
    result_label.pack(pady=10)

    buttons_frame = tk.Frame(root, bg="black")
    buttons_frame.pack(pady=20)

    create_buttons()

    effect_canvas = tk.Canvas(root, width=850, height=250,
                              bg="black", highlightthickness=0)
    effect_canvas.pack()

    tk.Button(root, text="🏅 Leaderboard",
              font=("Arial", 12, "bold"),
              bg="#ffaa00",
              command=show_leaderboard).pack(pady=5)

    tk.Button(root, text="🔁 New Game",
              font=("Arial", 14, "bold"),
              bg="#00ffcc",
              command=new_game).pack(pady=10)

    restart_btn = tk.Button(root,
                            text="🔁 Again Start",
                            font=("Arial",14,"bold"),
                            bg="#00ffcc",
                            command=new_game)

# ---------------- BUTTONS ----------------
letter_buttons = []
buttons_dict = {}

def create_buttons():
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    row=0; col=0
    for letter in letters:
        btn = tk.Button(buttons_frame,text=letter,width=4,height=2,
                        font=("Arial",12,"bold"),
                        bg="#1f1f1f",fg="#00ffcc",
                        command=lambda l=letter: guess_letter(l.lower()))
        btn.grid(row=row,column=col,padx=4,pady=4)
        letter_buttons.append(btn)
        buttons_dict[letter.lower()] = btn
        col+=1
        if col==9:
            col=0; row+=1

# ---------------- GAME LOGIC ----------------
def new_game():
    global word, guessed, wrong, score
    word=random.choice(words)
    guessed=[]
    wrong=0
    score=0
    result_label.config(text="")
    restart_btn.pack_forget()
    enable_buttons()
    update_display()

def update_display():
    display=" ".join([l if l in guessed else "_" for l in word])
    word_label.config(text=display)
    score_label.config(text=f"Score: {score}")
    attempts_label.config(text=f"Lives Left: {max_wrong-wrong}")
    highscore_label.config(text=f"{current_player} High: {high_scores.get(current_player,0)}")

def enable_buttons():
    for btn in letter_buttons:
        btn.config(state="normal",bg="#1f1f1f",fg="#00ffcc")

def disable_buttons():
    for btn in letter_buttons:
        btn.config(state="disabled")

# ---------------- ROCKET EFFECT ----------------
rainbow=["red","orange","yellow","green","cyan","blue","magenta"]

def fly_letter(button,letter,color):
    x=button.winfo_rootx()-root.winfo_rootx()+button.winfo_width()//2
    y=button.winfo_rooty()-root.winfo_rooty()+button.winfo_height()//2
    item=effect_canvas.create_text(x,y,text=letter.upper(),
                                   fill=color,font=("Arial",22,"bold"))
    animate_fly(item,x,y,0)

def animate_fly(item,x,y,step):
    if step<40:
        effect_canvas.move(item,0,-6)
        trail=effect_canvas.create_oval(x-3,y+6,x+3,y+12,
                                        fill=random.choice(rainbow),outline="")
        effect_canvas.move(trail,0,-6)
        root.after(150,lambda t=trail: effect_canvas.delete(t))
        y-=6
        root.after(30,animate_fly,item,x,y,step+1)
    else:
        explosion(x,y)
        effect_canvas.delete(item)

def explosion(x,y):
    for _ in range(25):
        size=random.randint(4,8)
        p=effect_canvas.create_oval(x,y,x+size,y+size,
                                    fill=random.choice(rainbow),outline="")
        dx=random.randint(-10,10)
        dy=random.randint(-10,10)
        animate_explosion(p,dx,dy,0)

def animate_explosion(p,dx,dy,step):
    if step<20:
        effect_canvas.move(p,dx,dy)
        root.after(30,animate_explosion,p,dx,dy,step+1)
    else:
        effect_canvas.delete(p)

# ---------------- SCREEN SHAKE ----------------
def screen_shake():
    for _ in range(10):
        x=random.randint(-10,10)
        y=random.randint(-10,10)
        root.geometry(f"+{x}+{y}")
        root.update()
    root.geometry("850x720")

# ---------------- GUESS ----------------
def guess_letter(letter):
    global wrong,score
    guessed.append(letter)
    btn=buttons_dict[letter]
    btn.config(state="disabled")

    if letter in word:
        winsound.Beep(1000,150)
        btn.config(bg="#00ffcc",fg="black")
        fly_letter(btn,letter,"#00ffcc")

        if all(l in guessed for l in word):
            score+=10
            result_label.config(text="🎉 YOU WON!",fg="#00ffcc")
            disable_buttons()
            save_high_score()
            restart_btn.pack(pady=10)

    else:
        winsound.Beep(400,200)
        wrong+=1
        btn.config(bg="red",fg="white")
        fly_letter(btn,letter,"red")
        screen_shake()

        if wrong>=max_wrong:
            result_label.config(text=f"💀 GAME OVER! Word was: {word}",fg="red")
            disable_buttons()
            restart_btn.pack(pady=10)

    update_display()

# ---------------- SAVE HIGH SCORE ----------------
def save_high_score():
    if score>high_scores.get(current_player,0):
        high_scores[current_player]=score
        with open("highscores.json","w") as f:
            json.dump(high_scores,f)

# ---------------- LEADERBOARD ----------------
def show_leaderboard():
    top=sorted(high_scores.items(),key=lambda x:x[1],reverse=True)[:5]
    board="🏅 TOP 5 PLAYERS\n\n"
    for i,(name,sc) in enumerate(top,1):
        board+=f"{i}. {name} - {sc}\n"

    popup=tk.Toplevel(root)
    popup.title("Leaderboard")
    popup.geometry("300x300")
    tk.Label(popup,text=board,font=("Arial",14)).pack(pady=20)

# ---------------- START ----------------
root.mainloop() 