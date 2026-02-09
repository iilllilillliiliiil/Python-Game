import customtkinter as ctk
import random
import math

class MafiaGameGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🌙 마피아 게임 🌞")
        self.geometry("800x600")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.players = []
        self.players_roles = {}
        self.alive = {}
        self.day = 1
        self.num_players = 0
        self.night_result = None
        self.suspicion = {}
        self.vote_vars = {}
        self.suspicion_vars = {}
        self.night_vars = {}
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(expand=True, fill="both")
        # 토론 타이머 관련 변수
        self.discussion_time = 0  # 실제 남은 시간(타이머용)
        self.discussion_time_setting = None  # 사용자가 입력한 토론 시간(초)
        self.discussion_timer_id = None
        self.discussion_time_label = None
        self.to_vote_btn = None
        self.show_player_count_input()

    def show_player_count_input(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        label = ctk.CTkLabel(self.main_frame, text="플레이어 수 입력 (4~6명)", font=("맑은 고딕", 28, "bold"))
        label.pack(pady=40)
        self.count_entry = ctk.CTkEntry(self.main_frame, width=120, font=("맑은 고딕", 22))
        self.count_entry.pack(pady=10)
        submit_btn = ctk.CTkButton(self.main_frame, text="확인", font=("맑은 고딕", 20), command=self.get_player_count)
        submit_btn.pack(pady=20)
        self.count_entry.bind("<Return>", lambda event: self.get_player_count())

    def get_player_count(self):
        try:
            num = int(self.count_entry.get())
            if 4 <= num <= 6:
                self.num_players = num
                self.players = []
                self.show_player_name_inputs()
            else:
                self.show_error("4명 이상 6명 이하로 입력해주세요.")
        except ValueError:
            self.show_error("숫자로 입력해주세요.")

    def show_error(self, msg):
        error_label = ctk.CTkLabel(self.main_frame, text=msg, text_color="red", font=("맑은 고딕", 18, "bold"))
        error_label.pack()
        self.after(1800, error_label.destroy)

    def show_player_name_inputs(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.name_entries = []
        label = ctk.CTkLabel(self.main_frame, text="플레이어 이름 입력", font=("맑은 고딕", 24, "bold"))
        label.pack(pady=25)
        for i in range(self.num_players):
            frame = ctk.CTkFrame(self.main_frame)
            frame.pack(pady=7)
            l = ctk.CTkLabel(frame, text=f"{i+1}번 플레이어:", width=120, anchor="e", font=("맑은 고딕", 18))
            l.pack(side="left")
            entry = ctk.CTkEntry(frame, width=180, font=("맑은 고딕", 18))
            entry.pack(side="left", padx=10)
            self.name_entries.append(entry)
        submit_btn = ctk.CTkButton(self.main_frame, text="역할 배정", font=("맑은 고딕", 20), command=self.assign_roles)
        submit_btn.pack(pady=30)
        if self.name_entries:
            self.name_entries[-1].bind("<Return>", lambda event: self.assign_roles())

    def assign_roles(self):
        self.players = []
        for entry in self.name_entries:
            name = entry.get().strip()
            if not name:
                self.show_error("모든 플레이어 이름을 입력해주세요.")
                return
            self.players.append(name)
        roles = ["마피아", "의사", "경찰"] + ["시민"] * (self.num_players - 3)
        random.shuffle(roles)
        self.players_roles = dict(zip(self.players, roles))
        self.alive = {p: True for p in self.players}
        self.show_roles()

    def show_roles(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        label = ctk.CTkLabel(self.main_frame, text="역할 배정 결과", font=("맑은 고딕", 24, "bold"))
        label.pack(pady=25)
        for p in self.players:
            role_label = ctk.CTkLabel(self.main_frame, text=f"{p}: {self.players_roles[p]}", font=("맑은 고딕", 20))
            role_label.pack()

        next_btn = ctk.CTkButton(self.main_frame, text="게임 시작", font=("맑은 고딕", 20), command=self.start_night_first)
        next_btn.pack(pady=40)

    def start_night_first(self):
        self.day = 1
        self.night_phase_gui()

    def start_day(self):
        self.morning_phase_gui()

    # 밤에 마피아 → 의사 → 경찰 순서로 지목하도록 구현
    def night_phase_gui(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.night_selected = {"mafia": None, "doctor": None, "police": None}
        self.night_step = 0  # 0: 마피아, 1: 의사, 2: 경찰
        self._night_phase_gui_step()

    def _night_phase_gui_step(self):
        # 현재 단계에 따라 화면을 다르게 보여줌
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        alive_players = [p for p in self.players if self.alive[p]]
        mafia_players = [p for p in alive_players if self.players_roles[p] == "마피아"]
        doctor_players = [p for p in alive_players if self.players_roles[p] == "의사"]
        police_players = [p for p in alive_players if self.players_roles[p] == "경찰"]

        canvas_size = 400
        player_radius = 40
        center_x = canvas_size // 2
        center_y = canvas_size // 2
        num = len(alive_players)
        circle_frame = ctk.CTkFrame(self.main_frame)
        circle_frame.pack(pady=20)
        night_canvas = ctk.CTkCanvas(circle_frame, width=canvas_size, height=canvas_size, bg="#222222", highlightthickness=0)
        night_canvas.pack()
        player_positions = {}
        night_oval_ids = {}
        angle_gap = 2 * math.pi / num if num > 0 else 0
        for idx, p in enumerate(alive_players):
            angle = angle_gap * idx - math.pi/2
            x = center_x + int(math.cos(angle) * 140)
            y = center_y + int(math.sin(angle) * 140)
            fill_color = "#4444FF" if self.players_roles[p] == "마피아" else "#44FF44" if self.players_roles[p] == "의사" else "#FFD700" if self.players_roles[p] == "경찰" else "#AAAAAA"
            oval_id = night_canvas.create_oval(
                x-player_radius, y-player_radius, x+player_radius, y+player_radius,
                fill=fill_color, outline="#FFFFFF", width=3, tags=("player_oval",)
            )
            night_canvas.create_text(x, y, text=p, fill="#FFFFFF", font=("맑은 고딕", 14, "bold"))
            player_positions[p] = (x, y)
            night_oval_ids[p] = oval_id

        # 단계별 안내 및 클릭 처리
        if self.night_step == 0:
            # 마피아 단계
            label = ctk.CTkLabel(self.main_frame, text=f"🌙 밤 {self.day} - 마피아({mafia_players[0] if mafia_players else ''})가 제외할 사람을 선택하세요.", font=("맑은 고딕", 22, "bold"), text_color="#FF2222")
            label.pack(pady=10)
            def on_click(event):
                clicked_player = None
                for p, (x, y) in player_positions.items():
                    if (x - event.x) ** 2 + (y - event.y) ** 2 <= player_radius ** 2:
                        clicked_player = p
                        break
                if not clicked_player or (mafia_players and clicked_player in mafia_players):
                    return
                self.night_selected["mafia"] = clicked_player
                # 하이라이트
                for p, oid in night_oval_ids.items():
                    night_canvas.itemconfig(oid, outline="#FFFFFF", width=3)
                night_canvas.itemconfig(night_oval_ids[clicked_player], outline="#FF2222", width=5)
                # 총 아이콘
                if mafia_players:
                    from_x, from_y = player_positions[mafia_players[0]]
                    to_x, to_y = player_positions[clicked_player]
                    night_canvas.delete("icon")
                    self.draw_gun_icon(night_canvas, from_x, from_y, to_x, to_y)
                # 다음 버튼 활성화
                next_btn.configure(state="normal")
            night_canvas.bind("<Button-1>", on_click)
            next_btn = ctk.CTkButton(self.main_frame, text="다음(의사)", font=("맑은 고딕", 20), state="disabled", command=self._night_next_step)
            next_btn.pack(pady=30)
        elif self.night_step == 1:
            # 의사 단계
            if not doctor_players:
                # 의사가 죽었으면 스킵
                label = ctk.CTkLabel(self.main_frame, text=f"🌙 밤 {self.day} - 의사가 사망하여 치료를 할 수 없습니다.", font=("맑은 고딕", 22, "bold"), text_color="#00BFFF")
                label.pack(pady=20)
                next_btn = ctk.CTkButton(self.main_frame, text="다음(경찰)", font=("맑은 고딕", 20), command=self._night_next_step)
                next_btn.pack(pady=30)
            else:
                label = ctk.CTkLabel(self.main_frame, text=f"🌙 밤 {self.day} - 의사({doctor_players[0]})가 보호할 사람을 선택하세요.", font=("맑은 고딕", 22, "bold"), text_color="#00BFFF")
                label.pack(pady=10)
                def on_click(event):
                    clicked_player = None
                    for p, (x, y) in player_positions.items():
                        if (x - event.x) ** 2 + (y - event.y) ** 2 <= player_radius ** 2:
                            clicked_player = p
                            break
                    if not clicked_player:
                        return
                    self.night_selected["doctor"] = clicked_player
                    # 하이라이트
                    for p, oid in night_oval_ids.items():
                        night_canvas.itemconfig(oid, outline="#FFFFFF", width=3)
                    night_canvas.itemconfig(night_oval_ids[clicked_player], outline="#00BFFF", width=5)
                    # 주사기 아이콘
                    if doctor_players:
                        from_x, from_y = player_positions[doctor_players[0]]
                        to_x, to_y = player_positions[clicked_player]
                        night_canvas.delete("icon")
                        self.draw_syringe_icon(night_canvas, from_x, from_y, to_x, to_y)
                    next_btn.configure(state="normal")
                night_canvas.bind("<Button-1>", on_click)
                next_btn = ctk.CTkButton(self.main_frame, text="다음(경찰)", font=("맑은 고딕", 20), state="disabled", command=self._night_next_step)
                next_btn.pack(pady=30)
        elif self.night_step == 2:
            # 경찰 단계
            if not police_players:
                # 경찰이 죽었으면 스킵
                label = ctk.CTkLabel(self.main_frame, text=f"🌙 밤 {self.day} - 경찰이 사망하여 조사를 할 수 없습니다.", font=("맑은 고딕", 22, "bold"), text_color="#FFD700")
                label.pack(pady=20)
                next_btn = ctk.CTkButton(self.main_frame, text="밤 결과 확인", font=("맑은 고딕", 20), command=self.show_night_result_gui)
                next_btn.pack(pady=30)
            else:
                label = ctk.CTkLabel(self.main_frame, text=f"🌙 밤 {self.day} - 경찰({police_players[0]})이 조사할 사람을 선택하세요.", font=("맑은 고딕", 22, "bold"), text_color="#FFD700")
                label.pack(pady=10)
                def on_click(event):
                    clicked_player = None
                    for p, (x, y) in player_positions.items():
                        if (x - event.x) ** 2 + (y - event.y) ** 2 <= player_radius ** 2:
                            clicked_player = p
                            break
                    if not clicked_player or (police_players and clicked_player == police_players[0]):
                        return
                    self.night_selected["police"] = clicked_player
                    # 하이라이트
                    for p, oid in night_oval_ids.items():
                        night_canvas.itemconfig(oid, outline="#FFFFFF", width=3)
                    night_canvas.itemconfig(night_oval_ids[clicked_player], outline="#FFD700", width=5)
                    # 돋보기 아이콘
                    if police_players:
                        from_x, from_y = player_positions[police_players[0]]
                        to_x, to_y = player_positions[clicked_player]
                        night_canvas.delete("icon")
                        self.draw_magnifier_icon(night_canvas, from_x, from_y, to_x, to_y)
                    next_btn.configure(state="normal")
                night_canvas.bind("<Button-1>", on_click)
                next_btn = ctk.CTkButton(self.main_frame, text="밤 결과 확인", font=("맑은 고딕", 20), state="disabled", command=self.show_night_result_gui)
                next_btn.pack(pady=30)

    def _night_next_step(self):
        self.night_step += 1
        self._night_phase_gui_step()

    def draw_gun_icon(self, canvas, from_x, from_y, to_x, to_y):
        canvas.create_line(from_x, from_y, to_x, to_y, fill="#FF2222", width=5, arrow="last", tags="icon")
        dx = to_x - from_x
        dy = to_y - from_y
        length = math.hypot(dx, dy)
        if length == 0:
            return
        ux, uy = dx/length, dy/length
        hx, hy = -uy, ux
        base_x = from_x + ux*30
        base_y = from_y + uy*30
        size = 12
        points = [
            (base_x + hx*size, base_y + hy*size),
            (base_x - hx*size, base_y - hy*size),
            (base_x - hx*size + ux*size, base_y - hy*size + uy*size),
            (base_x + hx*size + ux*size, base_y + hy*size + uy*size)
        ]
        canvas.create_polygon(points, fill="#333333", outline="#FF2222", tags="icon")
        bullet_x = to_x - ux*30
        bullet_y = to_y - uy*30
        canvas.create_oval(bullet_x-7, bullet_y-7, bullet_x+7, bullet_y+7, fill="#FF2222", outline="#FFAAAA", tags="icon")

    def draw_syringe_icon(self, canvas, from_x, from_y, to_x, to_y):
        canvas.create_line(from_x, from_y, to_x, to_y, fill="#00BFFF", width=4, arrow="last", tags="icon")
        dx = to_x - from_x
        dy = to_y - from_y
        length = math.hypot(dx, dy)
        if length == 0:
            return
        ux, uy = dx/length, dy/length
        hx, hy = -uy, ux
        base_x = from_x + ux*30
        base_y = from_y + uy*30
        size = 10
        points = [
            (base_x + hx*size, base_y + hy*size),
            (base_x - hx*size, base_y - hy*size),
            (base_x - hx*size + ux*size*2, base_y - hy*size + uy*size*2),
            (base_x + hx*size + ux*size*2, base_y + hy*size + uy*size*2)
        ]
        canvas.create_polygon(points, fill="#B0E0FF", outline="#00BFFF", tags="icon")
        cross_x = from_x + ux*15
        cross_y = from_y + uy*15
        canvas.create_line(cross_x-8, cross_y, cross_x+8, cross_y, fill="#00BFFF", width=3, tags="icon")
        canvas.create_line(cross_x, cross_y-8, cross_x, cross_y+8, fill="#00BFFF", width=3, tags="icon")

    def draw_magnifier_icon(self, canvas, from_x, from_y, to_x, to_y):
        dx = to_x - from_x
        dy = to_y - from_y
        length = math.hypot(dx, dy)
        if length == 0:
            return
        ux, uy = dx/length, dy/length
        lens_x = to_x - ux*30
        lens_y = to_y - uy*30
        r = 18
        canvas.create_oval(lens_x-r, lens_y-r, lens_x+r, lens_y+r, outline="#FFD700", width=4, fill="#FFFFAA", tags="icon")
        handle_x = lens_x - ux*20
        handle_y = lens_y - uy*20
        canvas.create_line(lens_x, lens_y, handle_x, handle_y, fill="#FFD700", width=5, tags="icon")

    def show_night_result_gui(self):
        alive_players = [p for p in self.players if self.alive[p]]
        mafia_target = self.night_selected["mafia"] if hasattr(self, "night_selected") else None

        # 의사/경찰이 죽었으면 night_selected에 None이 들어가도록 처리
        doctor_alive = any(self.players_roles[p] == "의사" and self.alive[p] for p in self.players)
        police_alive = any(self.players_roles[p] == "경찰" and self.alive[p] for p in self.players)
        doctor_save = self.night_selected["doctor"] if doctor_alive and hasattr(self, "night_selected") else None
        police_target = self.night_selected["police"] if police_alive and hasattr(self, "night_selected") else None

        police_name = None
        for p in alive_players:
            if self.players_roles[p] == "경찰":
                police_name = p
                break

        killed = None
        if mafia_target and mafia_target != doctor_save:
            self.alive[mafia_target] = False
            killed = mafia_target

        investigation = None
        if police_name and police_target:
            investigation = {
                "police": police_name,
                "target": police_target,
                "role": self.players_roles[police_target]
            }

        self.night_result = {
            "killed": killed,
            "saved": doctor_save,
            "mafia_target": mafia_target,
            "investigation": investigation
        }

        for widget in self.main_frame.winfo_children():
            widget.destroy()
        # 밤 결과 제목
        label = ctk.CTkLabel(self.main_frame, text=f"🌙 밤 {self.day} 결과 🌙", font=("맑은 고딕", 28, "bold"), text_color="#FFA500")
        label.pack(pady=(18, 8))

        # 밤 결과 요약 프레임 (왼쪽)
        result_frame = ctk.CTkFrame(self.main_frame)
        result_frame.pack(side="left", fill="y", padx=(30, 0), pady=18, expand=False)

        # 마피아가 처치한 사람 결과
        if mafia_target:
            mafia_label = ctk.CTkLabel(result_frame, text=f"마피아 처치 대상: {mafia_target}", font=("맑은 고딕", 19))
            mafia_label.pack(pady=4, anchor="w")
        else:
            mafia_label = ctk.CTkLabel(result_frame, text="마피아가 아무도 선택하지 않음", font=("맑은 고딕", 19))
            mafia_label.pack(pady=4, anchor="w")

        # 의사가 살린 사람 결과
        if doctor_alive and doctor_save:
            doctor_label = ctk.CTkLabel(result_frame, text=f"의사 치료 대상: {doctor_save}", font=("맑은 고딕", 19))
            doctor_label.pack(pady=4, anchor="w")
        elif not doctor_alive:
            doctor_label = ctk.CTkLabel(result_frame, text="의사 사망(치료 불가)", font=("맑은 고딕", 19))
            doctor_label.pack(pady=4, anchor="w")
        else:
            doctor_label = ctk.CTkLabel(result_frame, text="의사가 아무도 선택하지 않음", font=("맑은 고딕", 19))
            doctor_label.pack(pady=4, anchor="w")

        # 실제로 제거된 사람 결과
        if killed:
            killed_label = ctk.CTkLabel(result_frame, text=f"{killed}님이 마피아에게 제거됨", font=("맑은 고딕", 19, "bold"), text_color="#FF5555")
            killed_label.pack(pady=4, anchor="w")
        elif mafia_target:
            saved_label = ctk.CTkLabel(result_frame, text=f"{mafia_target}님은 의사 치료로 생존!", font=("맑은 고딕", 19, "bold"), text_color="#32CD32")
            saved_label.pack(pady=4, anchor="w")
        else:
            no_kill_label = ctk.CTkLabel(result_frame, text="아무도 제거되지 않음", font=("맑은 고딕", 19, "bold"))
            no_kill_label.pack(pady=4, anchor="w")

        # 경찰 조사 결과
        if police_alive and investigation:
            inv_label = ctk.CTkLabel(result_frame, text=f"경찰({investigation['police']}) 조사: {investigation['target']}({investigation['role']})", font=("맑은 고딕", 18))
            inv_label.pack(pady=4, anchor="w")
        elif not police_alive:
            inv_label = ctk.CTkLabel(result_frame, text="경찰 사망(조사 불가)", font=("맑은 고딕", 18))
            inv_label.pack(pady=4, anchor="w")
        else:
            inv_label = ctk.CTkLabel(result_frame, text="경찰 조사 결과 없음", font=("맑은 고딕", 18))
            inv_label.pack(pady=4, anchor="w")

        # 토론 시작 버튼 (밤 결과 요약 아래에 바로)
        next_btn = ctk.CTkButton(result_frame, text="낮 토론 시작", font=("맑은 고딕", 20), command=self.show_discussion_time_input)
        next_btn.pack(pady=(28, 0), anchor="w", fill="x")

        # 원 형태로 플레이어 배치 (밤 결과에도 표시, 오른쪽)
        circle_frame = ctk.CTkFrame(self.main_frame)
        circle_frame.pack(side="right", fill="both", expand=True, padx=(0, 30), pady=18)
        canvas_size = 400
        player_radius = 40
        center_x = canvas_size // 2
        center_y = canvas_size // 2
        num = len([p for p in self.players if self.alive[p] or p == killed])
        result_canvas = ctk.CTkCanvas(circle_frame, width=canvas_size, height=canvas_size, bg="#222222", highlightthickness=0)
        result_canvas.pack(expand=True)
        player_positions = {}
        angle_gap = 2 * math.pi / num if num > 0 else 0
        show_players = [p for p in self.players if self.alive[p] or p == killed]
        for idx, p in enumerate(show_players):
            angle = angle_gap * idx - math.pi/2
            x = center_x + int(math.cos(angle) * 130)
            y = center_y + int(math.sin(angle) * 130)
            fill_color = "#4444FF" if self.players_roles[p] == "마피아" else "#44FF44" if self.players_roles[p] == "의사" else "#FFD700" if self.players_roles[p] == "경찰" else "#AAAAAA"
            outline_color = "#FF5555" if p == killed else "#FFFFFF"
            width = 6 if p == killed else 3
            result_canvas.create_oval(
                x-player_radius, y-player_radius, x+player_radius, y+player_radius,
                fill=fill_color, outline=outline_color, width=width
            )
            result_canvas.create_text(x, y, text=p, fill="#FFFFFF", font=("맑은 고딕", 17, "bold"))
            player_positions[p] = (x, y)

        # 마피아 총
        if mafia_target and mafia_target in player_positions and mafia_target != doctor_save:
            mafia_players = [p for p in self.players if self.players_roles[p] == "마피아" and self.alive[p]]
            if mafia_players:
                from_x, from_y = player_positions[mafia_players[0]]
                to_x, to_y = player_positions[mafia_target]
                self.draw_gun_icon(result_canvas, from_x, from_y, to_x, to_y)
        # 의사 주사기
        if doctor_save and doctor_save in player_positions:
            doctor_players = [p for p in self.players if self.players_roles[p] == "의사" and self.alive[p]]
            if doctor_players:
                from_x, from_y = player_positions[doctor_players[0]]
                to_x, to_y = player_positions[doctor_save]
                self.draw_syringe_icon(result_canvas, from_x, from_y, to_x, to_y)
        # 경찰 돋보기
        if investigation and investigation["target"] in player_positions:
            police_players = [p for p in self.players if self.players_roles[p] == "경찰" and self.alive[p]]
            if police_players:
                from_x, from_y = player_positions[police_players[0]]
                to_x, to_y = player_positions[investigation["target"]]
                self.draw_magnifier_icon(result_canvas, from_x, from_y, to_x, to_y)

    def show_discussion_time_input(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        label = ctk.CTkLabel(self.main_frame, text="낮 토론 시간(초) 입력", font=("맑은 고딕", 24, "bold"))
        label.pack(pady=25)
        self.discussion_entry = ctk.CTkEntry(self.main_frame, width=120, font=("맑은 고딕", 22))
        if self.discussion_time_setting is not None:
            self.discussion_entry.insert(0, str(self.discussion_time_setting))
        else:
            self.discussion_entry.insert(0, "60")
        self.discussion_entry.pack(pady=10)
        submit_btn = ctk.CTkButton(self.main_frame, text="토론 시작", font=("맑은 고딕", 20), command=self.start_discussion_phase)
        submit_btn.pack(pady=20)
        self.discussion_entry.bind("<Return>", lambda event: self.start_discussion_phase())

    def start_discussion_phase(self):
        if self.discussion_time_setting is not None:
            self.discussion_time = self.discussion_time_setting
            self.show_discussion_timer()
            return
        try:
            t = int(self.discussion_entry.get())
            if t <= 0:
                self.show_error("1초 이상 입력해주세요.")
                return
            self.discussion_time_setting = t
            self.discussion_time = t
            self.show_discussion_timer()
        except ValueError:
            self.show_error("숫자로 입력해주세요.")

    def show_discussion_timer(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        label = ctk.CTkLabel(self.main_frame, text="🗣️ 낮 토론 시간 🗣️", font=("맑은 고딕", 26, "bold"), text_color="#32CD32")
        label.pack(pady=20)
        self.discussion_time_label = ctk.CTkLabel(self.main_frame, text=f"남은 시간: {self.discussion_time}초", font=("맑은 고딕", 32, "bold"), text_color="#FF8C00")
        self.discussion_time_label.pack(pady=30)
        self.to_vote_btn = ctk.CTkButton(self.main_frame, text="투표로 진행", font=("맑은 고딕", 20), command=self.goto_vote_from_discussion)
        self.to_vote_btn.pack(pady=30)
        self.update_discussion_timer()

    def update_discussion_timer(self):
        if self.discussion_time_label is None:
            return
        self.discussion_time_label.configure(text=f"남은 시간: {self.discussion_time}초")
        if self.discussion_time > 0:
            self.discussion_time -= 1
            self.discussion_timer_id = self.after(1000, self.update_discussion_timer)
        else:
            self.goto_vote_from_discussion()

    def goto_vote_from_discussion(self):
        if self.discussion_timer_id is not None:
            self.after_cancel(self.discussion_timer_id)
            self.discussion_timer_id = None
        self.day_vote_gui()

    def day_vote_gui(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        label = ctk.CTkLabel(self.main_frame, text="🗳️ 낮 투표 단계 🗳️", font=("맑은 고딕", 26, "bold"), text_color="#00BFFF")
        label.pack(pady=20)
        self.vote_vars = {}
        for player in self.players:
            if self.alive[player]:
                frame = ctk.CTkFrame(self.main_frame)
                frame.pack(pady=3)
                l = ctk.CTkLabel(frame, text=f"{player}의 투표:", width=120, anchor="e", font=("맑은 고딕", 16))
                l.pack(side="left")
                valid_targets = [p for p in self.players if self.alive[p] and p != player]
                var = ctk.StringVar(value=valid_targets[0] if valid_targets else "")
                menu = ctk.CTkOptionMenu(frame, variable=var, values=valid_targets, width=140, font=("맑은 고딕", 16))
                menu.pack(side="left", padx=10)
                self.vote_vars[player] = var

        submit_btn = ctk.CTkButton(self.main_frame, text="투표 집계", font=("맑은 고딕", 20), command=self.show_vote_result)
        submit_btn.pack(pady=30)

    def show_vote_result(self):
        votes = {p: var.get() for p, var in self.vote_vars.items() if var.get()}
        from collections import defaultdict
        vote_count = defaultdict(int)
        for v in votes.values():
            vote_count[v] += 1
        if not vote_count:
            removed = None
        else:
            max_votes = max(vote_count.values())
            candidates = [p for p, count in vote_count.items() if count == max_votes]
            removed = random.choice(candidates) if candidates else None
            if removed:
                self.alive[removed] = False

        for widget in self.main_frame.winfo_children():
            widget.destroy()
        label = ctk.CTkLabel(self.main_frame, text="🗳️ 낮 투표 결과 🗳️", font=("맑은 고딕", 26, "bold"), text_color="#00BFFF")
        label.pack(pady=20)
        summary = "\n".join([f"{voter} → {target}" for voter, target in votes.items()])
        summary_label = ctk.CTkLabel(self.main_frame, text=f"[투표 요약]\n{summary}", font=("맑은 고딕", 18))
        summary_label.pack(pady=10)
        if removed:
            removed_label = ctk.CTkLabel(self.main_frame, text=f"{removed} 플레이어가 제거되었습니다.", font=("맑은 고딕", 20, "bold"), text_color="#FF5555")
            removed_label.pack(pady=10)
        else:
            removed_label = ctk.CTkLabel(self.main_frame, text="아무도 제거되지 않았습니다.", font=("맑은 고딕", 20, "bold"))
            removed_label.pack(pady=10)
        self.check_game_over_gui()

    def check_game_over_gui(self):
        mafia_count = sum(1 for p in self.players if self.alive[p] and self.players_roles[p] == "마피아")
        # 경찰, 의사, 시민 수 각각 구해서 합치기
        police_count = sum(1 for p in self.players if self.alive[p] and self.players_roles[p] == "경찰")
        doctor_count = sum(1 for p in self.players if self.alive[p] and self.players_roles[p] == "의사")
        citizen_count = sum(1 for p in self.players if self.alive[p] and self.players_roles[p] == "시민")
        non_mafia_count = police_count + doctor_count + citizen_count

        if non_mafia_count == 0 and mafia_count > 0:
            winner = "마피아 승리"
            game_over = True
        elif mafia_count == 0:
            winner = "시민 승리"
            game_over = True
        elif mafia_count >= non_mafia_count:
            winner = "마피아 승리"
            game_over = True
        else:
            winner = None
            game_over = False

        if game_over:
            for widget in self.main_frame.winfo_children():
                widget.destroy()
            label = ctk.CTkLabel(self.main_frame, text=f"🎉 {winner}! 🎉", font=("맑은 고딕", 32, "bold"), text_color="#00FF00")
            label.pack(pady=60)
            end_btn = ctk.CTkButton(self.main_frame, text="메인 메뉴로", font=("맑은 고딕", 22), command=self.show_player_count_input)
            end_btn.pack(pady=30)
            self.discussion_time_setting = None
        else:
            next_btn = ctk.CTkButton(self.main_frame, text="다음 밤으로", font=("맑은 고딕", 20), command=self.next_night)
            next_btn.pack(pady=30)

    def next_night(self):
        self.day += 1
        self.night_phase_gui()

def run_mafia_game():
    app = MafiaGameGUI()
    app.mainloop()
    
if __name__ == "__main__":
    run_mafia_game()