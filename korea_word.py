import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import random
import time
import threading
import customtkinter as ctk
from tkinter import messagebox

API_KEY = "267281338A8C7B83636DD8BC6660150F"
BASE_URL = "https://krdict.korean.go.kr/api/search"

# ---------------- 두음법칙 변환 ----------------
# 두음법칙이 적용될 수 있는 대표적인 초성 쌍
DOOUM_RULES = {
    '라': ['나'], '락': ['낙'], '란': ['난'], '랄': ['날'], '람': ['남'], '랍': ['납'], '랑': ['낭'],
    '래': ['내'], '랭': ['냉'], '려': ['여'], '력': ['역'], '련': ['연'], '렬': ['열'], '렴': ['염'],
    '렵': ['엽'], '령': ['영'], '례': ['예'], '로': ['노'], '록': ['녹'], '론': ['논'], '롱': ['농'],
    '뢰': ['뇌'], '료': ['요'], '루': ['누'], '류': ['유'], '륙': ['육'], '륜': ['윤'], '률': ['율'],
    '륭': ['융'], '륵': ['늑'], '름': ['늠'], '릉': ['능'], '리': ['이']
}

def get_possible_initials(char):
    # 두음법칙 적용 가능한 모든 초성 반환
    initials = [char]
    for k, vlist in DOOUM_RULES.items():
        if char == k:
            initials.extend(vlist)
        elif char in vlist:
            initials.append(k)
    return list(set(initials))

# ---------------- API 호출 ----------------
def fetch_words(query, start=1, num=100):
    params = {
        "key": API_KEY,
        "q": query,
        "part": "word",
        "pos": 1,
        "letter_s": 3,
        "letter_e": 3,
        "sort": "dict",
        "start": start,
        "num": num
    }
    url = BASE_URL + "?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url) as response:
            data = response.read()
    except Exception as e:
        print("⚠️ API 요청 실패:", e)
        return [], 0

    root = ET.fromstring(data)
    words = []
    total = int(root.findtext("total", default="0"))
    for item in root.findall("item"):
        word_elem = item.find("word")
        pos_elem = item.find("pos")
        word = word_elem.text if word_elem is not None else None
        pos = pos_elem.text if pos_elem is not None else None
        if word and pos == "명사" and len(word) == 3:
            words.append(word)
    return words, total

def fetch_all_words(query):
    # query가 리스트면 각각 다 긁어서 합침
    if isinstance(query, list):
        all_words = []
        for q in query:
            all_words.extend(fetch_all_words(q))
        return list(set(all_words))
    all_words = []
    start = 1
    num = 100
    # 첫 요청
    words, total = fetch_words(query, start, num)
    all_words.extend(words)
    # 모든 페이지를 순회하여 전부 가져오기
    while start + num <= total:
        start += num
        time.sleep(0.1)
        words, _ = fetch_words(query, start, num)
        all_words.extend(words)
    # 마지막 남은 페이지가 있을 수 있으니 한 번 더 요청
    if start + num > total and start < total:
        start = total - (total - 1) % num
        words, _ = fetch_words(query, start, num)
        all_words.extend(words)
    return list(set(all_words))

def is_real_word(word):
    # 실제 국어사전에 등재된 3음절 명사인지 확인
    words, total = fetch_words(word, 1, 100)
    return word in words

# ---------------- 두음법칙 변환 ----------------
def get_all_dooeum_variants(word):
    # 첫글자 두음법칙 변환
    variants = set()
    initials = get_possible_initials(word[0])
    for ini in initials:
        variants.add(ini + word[1:])
    return list(variants)

# ---------------- 끝말잇기 규칙 체크 함수 ----------------
def is_valid_word_chain(prev_word, next_word):
    """
    prev_word의 마지막 글자와 next_word의 첫 글자가 두음법칙을 고려해 올바른지 체크
    """
    if not prev_word or not next_word:
        return False
    last_char = prev_word[-1]
    first_char = next_word[0]
    # 두음법칙 적용 가능한 모든 초성
    possible_initials = get_possible_initials(last_char)
    return first_char in possible_initials

# ---------------- GUI ----------------
class WordGameGUI:
    def __init__(self, root):
        self.root = root
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")
        self.used_words = set()
        self.current_word = None
        self.time_left = 10.0
        self.timer_running = False
        self.computer_thinking = False
        self.timer_id = None 

        root.title("🌟 끝말잇기 게임 🌟")
        root.geometry("700x750")
        root.resizable(False, False)

        # 배경 프레임
        self.bg_frame = ctk.CTkFrame(root, fg_color="#232946")
        self.bg_frame.pack(fill="both", expand=True)

        # 상단 타이틀
        self.title_label = ctk.CTkLabel(
            self.bg_frame, 
            text="✨ 끝말잇기 ✨", 
            font=("맑은 고딕", 32, "bold"), 
            text_color="#eebbc3"
        )
        self.title_label.pack(pady=(30, 10))

        # 안내 라벨
        self.label = ctk.CTkLabel(
            self.bg_frame, 
            text="룰: 3음절 명사, 중복 불가, 10초 제한", 
            font=("맑은 고딕", 16, "bold"),
            text_color="#b8c1ec"
        )
        self.label.pack(pady=5)

        # 메시지 로그 (화려한 테두리)
        self.log_frame = ctk.CTkFrame(self.bg_frame, fg_color="#393e46", border_width=3, border_color="#eebbc3")
        self.log_frame.pack(pady=15)
        self.log = ctk.CTkTextbox(self.log_frame, width=640, height=320, font=("맑은 고딕", 15), fg_color="#232946", text_color="#f6f6f6")
        self.log.pack(padx=5, pady=5)
        self.log.configure(state="disabled")

        # 입력창 + 버튼 (화려한 프레임)
        entry_frame = ctk.CTkFrame(self.bg_frame, fg_color="#393e46", border_width=2, border_color="#b8c1ec")
        entry_frame.pack(pady=15)

        self.entry = ctk.CTkEntry(entry_frame, width=250, height=40, font=("맑은 고딕", 16), placeholder_text="단어 입력", fg_color="#232946", text_color="#eebbc3", border_color="#eebbc3", border_width=2)
        self.entry.grid(row=0, column=0, padx=8, pady=8)
        self.entry.bind("<Return>", lambda event: self.submit_word())

        self.submit_button = ctk.CTkButton(
            entry_frame, text="🚀 제출", width=120, height=40, 
            font=("맑은 고딕", 15, "bold"), fg_color="#eebbc3", text_color="#232946", hover_color="#b8c1ec",
            command=self.submit_word
        )
        self.submit_button.grid(row=0, column=1, padx=8, pady=8)

        self.restart_button = ctk.CTkButton(
            entry_frame, text="🔄 재시작", width=120, height=40, 
            font=("맑은 고딕", 15, "bold"), fg_color="#b8c1ec", text_color="#232946", hover_color="#eebbc3",
            command=self.restart_game, state="disabled"
        )
        self.restart_button.grid(row=0, column=2, padx=8, pady=8)

        # 타이머 (화려한 원형 프로그레스바와 라벨)
        timer_frame = ctk.CTkFrame(self.bg_frame, fg_color="#232946")
        timer_frame.pack(pady=10)

        self.timer_label = ctk.CTkLabel(
            timer_frame, text="남은 시간 : 10.0초", 
            font=("맑은 고딕", 18, "bold"), text_color="#eebbc3"
        )
        self.timer_label.pack(pady=5)

        self.progress = ctk.CTkProgressBar(
            timer_frame, width=500, height=20, 
            progress_color="#eebbc3", fg_color="#393e46", border_color="#b8c1ec", border_width=2
        )
        self.progress.set(1.0)
        self.progress.pack(pady=5)

        # 현재 단어 표시 (화려한 라벨)
        self.current_word_label = ctk.CTkLabel(
            self.bg_frame, text="현재 단어 : 없음", 
            font=("맑은 고딕", 20, "bold"), text_color="#f6f6f6"
        )
        self.current_word_label.pack(pady=10)

        # "컴퓨터 생각 중..." 표시용 라벨 추가
        self.computer_thinking_label = ctk.CTkLabel(
            self.bg_frame, text="", 
            font=("맑은 고딕", 18, "bold"), text_color="#b8c1ec"
        )
        self.computer_thinking_label.pack(pady=2)

        # 하단 크레딧
        self.credit_label = ctk.CTkLabel(
            self.bg_frame, text="made by KB | 실시간 국립국어원 API", 
            font=("맑은 고딕", 12), text_color="#b8c1ec"
        )
        self.credit_label.pack(side="bottom", pady=10)

        self.log_message("🌈 게임 시작! 첫 단어를 입력하세요.")
        self.start_timer()

    def log_message(self, msg, replace_last=False):
        self.log.configure(state="normal")
        if replace_last:
            # 지우고 마지막 줄에 새로 씀
            self.log.delete("end-2l", "end-1l")
            self.log.insert("end", msg + "\n")
        else:
            self.log.insert("end", msg + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")



    def start_timer(self):
        # 기존 타이머가 있으면 취소
        if self.timer_id is not None:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        self.timer_running = False
        self.time_left = 10.0
        self.progress.set(1.0)
        self.timer_running = True
        self.update_timer()

    def update_timer(self):
        if not self.timer_running or self.computer_thinking:
            # 타이머가 멈췄거나 컴퓨터가 생각 중이면 타이머를 다시 예약하지 않음
            return
        self.timer_label.configure(text=f"남은 시간 : {self.time_left:.1f}초")
        self.progress.set(self.time_left / 10.0)
        if self.time_left > 0:
            self.time_left -= 0.1
            self.timer_id = self.root.after(100, self.update_timer)
        else:
            self.timer_running = False
            self.timer_id = None
            self.log_message("⏰ 시간 초과! 당신의 패배!")
            messagebox.showinfo("게임 종료", "⏰ 시간 초과! 게임이 끝났습니다.")
            self.end_game()

    def submit_word(self):
        if self.computer_thinking:
            return
        user_word = self.entry.get().strip()
        self.entry.delete(0, "end")

        if not user_word:
            return
        if len(user_word) != 3:
            self.log_message("⚠️ 3음절 명사만 입력하세요!")
            return
        if user_word in self.used_words:
            self.log_message("⚠️ 이미 사용한 단어입니다!")
            self.end_game()
            return

        # 실제 존재하는 3음절 명사인지 확인
        if not is_real_word(user_word):
            self.log_message("⚠️ 국어사전에 없는 단어입니다!")
            self.end_game()
            return

        # 두음법칙 적용
        if self.current_word:
            if not is_valid_word_chain(self.current_word, user_word):
                self.log_message("⚠️ 올바른 글자로 시작하지 않았습니다!")
                self.end_game()
                return

        self.used_words.add(user_word)
        self.current_word = user_word
        self.current_word_label.configure(text=f"현재 단어 : {user_word}", text_color="#eebbc3")
        self.log_message(f"🙋 사용자 : {user_word}")

        threading.Thread(target=self.computer_turn, args=(user_word,)).start()

    def computer_turn(self, prev_word):
        self.computer_thinking = True
        # 타이머 일시정지: 타이머가 돌고 있다면 멈춤
        if self.timer_id is not None:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

        self.root.after(0, lambda: self.current_word_label.configure(text="🤖 컴퓨터가 단어를 찾는 중...", text_color="#b8c1ec"))

        def _think():
            last_char = prev_word[-1]
            initials = get_possible_initials(last_char)
            candidates = []
            for ini in initials:
                words = fetch_all_words(ini)
                for w in words:
                    # 후보 단어가 이미 사용된 단어가 아니고, 실제 단어이며, 끝말잇기 규칙에 맞는지 체크
                    if w not in self.used_words and is_real_word(w):
                        if is_valid_word_chain(prev_word, w):
                            candidates.append(w)
            time.sleep(1)

            if not candidates:
                self.root.after(0, lambda: self.computer_thinking_label.configure(text=""))  # "컴퓨터 생각 중..." 라벨 지움
                self.root.after(0, lambda: self.log_message(f"🎉 '{last_char}'로 시작하는 단어가 없습니다. 당신의 승리!"))
                self.root.after(0, lambda: self.current_word_label.configure(text="🎉 당신의 승리!", text_color="#eebbc3"))
                self.root.after(0, lambda: messagebox.showinfo("게임 종료", "🎉 당신의 승리!"))
                self.root.after(0, self.end_game)
            else:
                computer_word = random.choice(candidates)
                self.used_words.add(computer_word)
                self.current_word = computer_word
                # 컴퓨터가 단어를 내는 순간 "컴퓨터 생각 중..." 라벨을 지움
                self.root.after(0, lambda: self.computer_thinking_label.configure(text=""))
                self.root.after(0, lambda: self.log_message(f"🤖 컴퓨터 : {computer_word}"))
                self.root.after(0, lambda: self.current_word_label.configure(text=f"현재 단어 : {computer_word}", text_color="#b8c1ec"))

            self.computer_thinking = False
            self.root.after(0, self.start_timer)

        threading.Thread(target=_think).start()

    def end_game(self):
        self.timer_running = False
        self.computer_thinking = False
        # 타이머가 돌고 있다면 취소
        if self.timer_id is not None:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        self.entry.configure(state="disabled")
        self.submit_button.configure(state="disabled")
        self.restart_button.configure(state="normal")
        self.current_word_label.configure(text="게임 종료!", text_color="#eebbc3")
        self.computer_thinking_label.configure(text="")  # 게임 종료시 "컴퓨터 생각 중..." 라벨도 지움

    def restart_game(self):
        self.used_words.clear()
        self.current_word = None
        self.entry.configure(state="normal")
        self.submit_button.configure(state="normal")
        self.restart_button.configure(state="disabled")
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")
        self.current_word_label.configure(text="현재 단어 : 없음", text_color="#f6f6f6")
        self.computer_thinking_label.configure(text="")  # 재시작시 "컴퓨터 생각 중..." 라벨도 지움
        self.log_message("🌈 게임 재시작! 첫 단어를 입력하세요.")
        self.start_timer()

def play_game():
    """끝말잇기 게임을 실행하는 함수"""
    root = ctk.CTk()
    game = WordGameGUI(root)
    root.mainloop()

if __name__ == "__main__":
    play_game()