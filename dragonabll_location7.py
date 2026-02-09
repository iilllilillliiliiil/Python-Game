import pygame
import sys
import threading
import os
import time
import random
import threading, queue  # 추가 부분 PM10:19


# 기존 완성된 게임 함수 import
from game import game_a                  # 가위바위보
from korea_word import play_game         # 끝말잇기
from mafia_game import run_mafia_game  # 마피아 게임

# -------------------------------------------------------
# 설정값 (현재 파일 위치 기준)
# -------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAP_FILE   = os.path.join(BASE_DIR, "A.png")
GOKU_FILE  = os.path.join(BASE_DIR, "b.png")
ROOMa_FILE = os.path.join(BASE_DIR, "rooma.png")
ROOMb_FILE = os.path.join(BASE_DIR, "roomb.png")
ROOMc_FILE = os.path.join(BASE_DIR, "roomc.png")

SPEED = 280
RUN_MULT = 1.8
START_POS = "center"  # "center" or "bottom_center"

# 방 크기/위치
ROOMa_SIZE, ROOMa_POS = (120, 100), (30, 180)
ROOMb_SIZE, ROOMb_POS = (120, 100), (395, 69)
ROOMc_SIZE, ROOMc_POS = (140, 110), (770, 826)

# -------------------------------------------------------
# GUI 맵 + 이동 + 게임 실행
# -------------------------------------------------------
def main():
    pygame.init()
    pygame.display.set_caption("게임 박스 맵 이동")

    # 맵 로드 및 화면 초기화
    map_img_raw = pygame.image.load(MAP_FILE)
    map_w, map_h = map_img_raw.get_width(), map_img_raw.get_height()
    screen = pygame.display.set_mode((map_w, map_h))
    map_img = map_img_raw.convert()

    # 캐릭터 로드 + 스케일
    goku_img_raw = pygame.image.load(GOKU_FILE).convert_alpha()
    target_h = max(32, int(map_h * 0.10))
    scale_ratio = target_h / goku_img_raw.get_height()
    goku_img = pygame.transform.smoothscale(
        goku_img_raw,
        (int(goku_img_raw.get_width() * scale_ratio), target_h)
    )
    goku_rect = goku_img.get_rect()
    if START_POS == "bottom_center":
        goku_rect.midbottom = (map_w // 2, map_h - 10)
    else:
        goku_rect.center = (map_w // 2, map_h // 2)

    debug_doors = False
    rooms = []

    def clamp_room_pos(rect):
        if rect.right > map_w: rect.x = max(0, map_w - rect.width)
        if rect.bottom > map_h: rect.y = max(0, map_h - rect.height)
        if rect.x < 0: rect.x = 0
        if rect.y < 0: rect.y = 0
        return rect

    def compute_door(rect):
        return pygame.Rect(rect.centerx - 22, rect.bottom - 16, 44, 16)

    def add_room(img_path, size, pos, label, game_func):
        img = pygame.image.load(img_path).convert_alpha()
        img = pygame.transform.smoothscale(img, size)
        rect = img.get_rect()
        rect.topleft = pos
        rect = clamp_room_pos(rect)
        door = compute_door(rect)
        rooms.append({
            "label": label,
            "img": img,
            "rect": rect,
            "door": door,
            "game": game_func,
            "inside": False,
            "started": False,
            "game_thread": None  # 새 필드 : 방별 스레드 추가 PM.09:58
        })

    # 기존 CLI 게임 함수로 대체
    add_room(ROOMa_FILE, ROOMa_SIZE, ROOMa_POS, 'A', game_a)
    add_room(ROOMb_FILE, ROOMb_SIZE, ROOMb_POS, 'B', play_game)
    add_room(ROOMc_FILE, ROOMc_SIZE, ROOMc_POS, 'C', run_mafia_game)

    clock = pygame.time.Clock()
    running = True
    active_thread = None

    print("캐릭터 이동: 화살표/WASD")
    print("roomA → 가위바위보, roomB → 끝말잇기, roomC → 마피아 게임")
    print("F1 → 문(door) 박스 디버그 표시 토글")

    while running:
        dt = clock.tick(120) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_F1:
                    debug_doors = not debug_doors

        # 이동 처리
        keys = pygame.key.get_pressed()
        mul = RUN_MULT if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) else 1.0
        vx = vy = 0.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: vx -= SPEED * mul
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: vx += SPEED * mul
        if keys[pygame.K_UP] or keys[pygame.K_w]: vy -= SPEED * mul
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: vy += SPEED * mul
        goku_rect.x += int(vx * dt)
        goku_rect.y += int(vy * dt)
        goku_rect.clamp_ip(screen.get_rect())

        # 방 진입/이탈 처리
        for r in rooms:
            now_inside = goku_rect.colliderect(r["door"])
            # 방 진입
            if now_inside and not r["inside"]: # 기존 다른 방의 스레드가 돌고있다면 정리되는 구간
                for other in rooms:
                    if other is not r and other["game_thread"] and other["game_thread"].is_alive():
                        print(f"[알림] room{other['label']} 게임 자동 종료 처리")
                        other["started"] = False
                        other["game_thread"] = None
                        #for문부터 5줄 추가부분, 스레드를 완전히 끌수없으니, stated 플래그만 끄고 무시하는 기능
                #if (active_thread is None) or (not active_thread.is_alive()): 불필요한 명령어
                if not r["started"]:
                        print(f"\n[알림] room{r['label']} 진입 -> 게임 시작!")
                        r["game_thread"] = threading.Thread(target=r["game"], daemon=True)
                        r["game_thread"].start()
                        # active_thread 제거를 해야 독립적으로 방을 드리 들어가짐 
                        #active_thread = threading.Thread(target=r["game"], daemon=True) 독립적인 게임 스레드가 아님 수정
                        #active_thread.start()
                        r["started"] = True
                r["inside"] = True
            elif not now_inside and r["inside"]:
                r["inside"] = False
                # 게임 스레드 종료 여부와 관계없이, 다시 들어가면 게임 재실행 기능 
                r["started"] = False

        # 화면 그리기
        screen.blit(map_img, (0, 0))
        for r in rooms:
            screen.blit(r["img"], r["rect"])
            if debug_doors:
                pygame.draw.rect(screen, (255, 0, 0), r["door"], 1)
        screen.blit(goku_img, goku_rect)
        pygame.display.flip()

    pygame.quit()
    sys.exit(0)

if __name__ == "__main__":
    main()
