import random
import sys
import customtkinter as ctk
from PIL import Image, ImageTk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class RPSGameFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.choices = ["가위", "바위", "보"]
        self.emoji = {"가위": "✌️", "바위": "✊", "보": "✋"}
        self.win_conditions = {("가위", "보"), ("바위", "가위"), ("보", "바위")}
        self.user_score = 0
        self.comp_score = 0
        self.draw_count = 0
        self.configure(fg_color="#222831")
        self.create_widgets()

    def create_widgets(self):
        # 타이틀
        self.title_label = ctk.CTkLabel(self, text="가위 바위 보", font=("나눔스퀘어", 36, "bold"), text_color="#00FFF0")
        self.title_label.pack(pady=(30, 10))

        # 점수판
        self.score_frame = ctk.CTkFrame(self, fg_color="#393E46")
        self.score_frame.pack(pady=(5, 15))
        self.user_score_label = ctk.CTkLabel(self.score_frame, text="나: 0", font=("나눔스퀘어", 20, "bold"), text_color="#FFD369")
        self.user_score_label.grid(row=0, column=0, padx=30, pady=10)
        self.draw_label = ctk.CTkLabel(self.score_frame, text="무: 0", font=("나눔스퀘어", 20, "bold"), text_color="#AAAAAA")
        self.draw_label.grid(row=0, column=1, padx=30, pady=10)
        self.comp_score_label = ctk.CTkLabel(self.score_frame, text="컴퓨터: 0", font=("나눔스퀘어", 20, "bold"), text_color="#FF6363")
        self.comp_score_label.grid(row=0, column=2, padx=30, pady=10)

        # 선택 버튼
        self.choices_frame = ctk.CTkFrame(self, fg_color="#393E46")
        self.choices_frame.pack(pady=10)
        self.buttons = []
        for idx, name in enumerate(self.choices):
            btn = ctk.CTkButton(
                self.choices_frame,
                text=f"{self.emoji[name]}\n{name}",
                width=120,
                height=90,
                font=("나눔스퀘어", 22, "bold"),
                fg_color="#00ADB5",
                hover_color="#00FFF0",
                command=lambda i=idx: self.play(i)
            )
            btn.grid(row=0, column=idx, padx=20, pady=10)
            self.buttons.append(btn)

        # 결과 애니메이션/라벨
        self.result_frame = ctk.CTkFrame(self, fg_color="#222831")
        self.result_frame.pack(pady=(20, 10))
        self.user_choice_label = ctk.CTkLabel(self.result_frame, text="", font=("나눔스퀘어", 32, "bold"))
        self.user_choice_label.grid(row=0, column=0, padx=30)
        self.vs_label = ctk.CTkLabel(self.result_frame, text="VS", font=("나눔스퀘어", 28, "bold"), text_color="#00FFF0")
        self.vs_label.grid(row=0, column=1, padx=10)
        self.comp_choice_label = ctk.CTkLabel(self.result_frame, text="", font=("나눔스퀘어", 32, "bold"))
        self.comp_choice_label.grid(row=0, column=2, padx=30)

        self.result_label = ctk.CTkLabel(self, text="", font=("나눔스퀘어", 26, "bold"))
        self.result_label.pack(pady=(10, 20))

        # 리셋/종료 버튼
        self.bottom_frame = ctk.CTkFrame(self, fg_color="#222831")
        self.bottom_frame.pack(pady=(10, 10))
        self.reset_btn = ctk.CTkButton(self.bottom_frame, text="점수 초기화", fg_color="#393E46", font=("나눔스퀘어", 16, "bold"), command=self.reset_score)
        self.reset_btn.grid(row=0, column=0, padx=20)
        self.exit_btn = ctk.CTkButton(self.bottom_frame, text="게임 종료", fg_color="#FF6363", font=("나눔스퀘어", 16, "bold"), command=self.quit_app)
        self.exit_btn.grid(row=0, column=1, padx=20)

    def play(self, user_idx):
        user_choice = self.choices[user_idx]
        comp_choice = random.choice(self.choices)
        self.user_choice_label.configure(text=f"{self.emoji[user_choice]}\n{user_choice}", text_color="#FFD369")
        self.comp_choice_label.configure(text=f"{self.emoji[comp_choice]}\n{comp_choice}", text_color="#FF6363")

        if user_choice == comp_choice:
            result = "무승부!"
            color = "#FFD369"
            self.draw_count += 1
        elif (user_choice, comp_choice) in self.win_conditions:
            result = "승리! 🎉"
            color = "#00FFB4"
            self.user_score += 1
        else:
            result = "패배! 😅"
            color = "#FF6363"
            self.comp_score += 1

        self.result_label.configure(text=f"결과: {result}", text_color=color)
        self.update_score_labels()

    def update_score_labels(self):
        self.user_score_label.configure(text=f"나: {self.user_score}")
        self.comp_score_label.configure(text=f"컴퓨터: {self.comp_score}")
        self.draw_label.configure(text=f"무: {self.draw_count}")

    def reset_score(self):
        self.user_score = 0
        self.comp_score = 0
        self.draw_count = 0
        self.result_label.configure(text="")
        self.user_choice_label.configure(text="")
        self.comp_choice_label.configure(text="")
        self.update_score_labels()

    def quit_app(self):
        self.master.destroy()
        sys.exit(0)

# -----------------------------
# 메인 앱 클래스 (가위바위보 단독)
# -----------------------------
class RPSGameApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("가위 바위 보 (customtkinter GUI)")
        self.geometry("600x600")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.rps_frame = RPSGameFrame(self)
        self.rps_frame.pack(fill="both", expand=True)

    def on_close(self):
        self.destroy()
        sys.exit(0)

# 게임 실행 함수 (dragonabll_location7.py에서 import용)
def game_a():
    """가위바위보 게임 실행 함수"""
    app = RPSGameApp()
    app.mainloop()

if __name__ == "__main__":
    game_a()