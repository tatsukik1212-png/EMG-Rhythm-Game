import pygame
import random
import sys
import serial
import time

# =========================================
# 基本設定
# =========================================
SCREEN_W, SCREEN_H = 1000, 700

FPS = 60
NOTE_SPEED = 5

ARM_NOTE_SIZE = (145, 185)
CHEST_NOTE_SIZE = (115, 105)

BODY_SIZE = (500, 500)

BODY_Y_OFFSET = 140
BODY_X_OFFSET = 160

SPAWN_MIN = 120
SPAWN_MAX = 200

LANE_OFFSET_X = 160

PERFECT_RANGE = 15
GOOD_RANGE = 35

THRESHOLD = 600

# =========================================
# レーン位置
# =========================================
LANES = {
    "left_arm":    (328, 345),
    "right_arm":   (675, 345),
    "left_chest":  (444, 410),
    "right_chest": (560, 405),
}

# =========================================
# 筋肉名
# =========================================
MUSCLE_NAMES = {
    "left_arm": "Left Arm",
    "right_arm": "Right Arm",
    "left_chest": "Left Chest",
    "right_chest": "Right Chest",
}

# =========================================
# 初期化
# =========================================
pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("MMC RHYTHM GAME")

clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 26)
big_font = pygame.font.SysFont(None, 58)
title_font = pygame.font.SysFont(None, 48)

# =========================================
# Arduino接続
# =========================================
try:

    ser_arm = serial.Serial("COM5", 115200)
    ser_chest = serial.Serial("COM4", 115200)

    time.sleep(2)

except Exception as e:

    print("Serial Error:", e)
    sys.exit()

# =========================================
# 画像読み込み
# =========================================
def load_img(path, size=None):

    img = pygame.image.load(path).convert_alpha()

    if size:
        img = pygame.transform.smoothscale(img, size)

    return img


body_img = load_img("source/rsc/body.png", BODY_SIZE)

muscle_imgs = {
    "left_arm": load_img("source/rsc/left_arm.png", ARM_NOTE_SIZE),
    "right_arm": load_img("source/rsc/right_arm.png", ARM_NOTE_SIZE),
    "left_chest": load_img("source/rsc/left_chest.png", CHEST_NOTE_SIZE),
    "right_chest": load_img("source/rsc/right_chest.png", CHEST_NOTE_SIZE),
}

# MISS画像
takuma_img = load_img("source/rsc/takuma.png", (155, 185))

# PERFECT画像
nakayama_img = load_img("source/rsc/nakayama.png", (155, 185))

# =========================================
# レーン描画
# =========================================
def draw_lanes(active_lanes):

    for lane in active_lanes:

        x, y = LANES[lane]

        lx = x + LANE_OFFSET_X

        pygame.draw.line(
            screen,
            (0, 140, 255),
            (lx, 0),
            (lx, SCREEN_H),
            2
        )

        pygame.draw.circle(
            screen,
            (0, 200, 255),
            (lx, y),
            6
        )

# =========================================
# ノーツ
# =========================================
class Note:

    def __init__(self, lane):

        self.lane = lane

        base_x, self.hit_y = LANES[lane]

        self.x = base_x + LANE_OFFSET_X

        self.y = -120

        self.active = True

    def update(self):

        self.y += NOTE_SPEED

        if self.y > SCREEN_H:

            self.active = False

            return "MISS"

        return None

    def draw(self):

        img = muscle_imgs[self.lane]

        rect = img.get_rect(center=(self.x, self.y))

        screen.blit(img, rect)

    def judge(self):

        diff = abs(self.y - self.hit_y)

        if diff <= PERFECT_RANGE:
            return "PERFECT"

        elif diff <= GOOD_RANGE:
            return "GOOD"

        return None

# =========================================
# 筋肉選択画面
# =========================================
def select_muscles():

    selected = []

    while True:

        screen.fill((0, 0, 0))

        title = big_font.render(
            "SELECT MUSCLE",
            True,
            (255, 255, 255)
        )

        screen.blit(
            title,
            (
                SCREEN_W // 2 - title.get_width() // 2,
                25
            )
        )

        for i, key in enumerate(MUSCLE_NAMES):

            x = SCREEN_W // 2 - 140 + (i % 2) * 280
            y = SCREEN_H // 2 - 120 + (i // 2) * 220

            img = muscle_imgs[key]

            rect = img.get_rect(center=(x, y))

            screen.blit(img, rect)

            name = font.render(
                MUSCLE_NAMES[key],
                True,
                (255, 255, 0)
            )

            screen.blit(
                name,
                (x - name.get_width() // 2, y + 90)
            )

            if key in selected:

                pygame.draw.rect(
                    screen,
                    (0, 255, 0),
                    rect.inflate(20, 20),
                    5,
                    border_radius=10
                )

        info = font.render(
            "CLICK 2 MUSCLES - PRESS ENTER",
            True,
            (180,180,180)
        )

        screen.blit(
            info,
            (
                SCREEN_W//2 - info.get_width()//2,
                SCREEN_H - 60
            )
        )

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:

                mx, my = event.pos

                for i, key in enumerate(MUSCLE_NAMES):

                    x = SCREEN_W // 2 - 140 + (i % 2) * 280
                    y = SCREEN_H // 2 - 120 + (i // 2) * 220

                    rect = muscle_imgs[key].get_rect(center=(x, y))

                    if rect.collidepoint(mx, my):

                        if key in selected:

                            selected.remove(key)

                        elif len(selected) < 2:

                            selected.append(key)

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_RETURN and len(selected) == 2:

                    return selected

        pygame.display.flip()

        clock.tick(FPS)

# =========================================
# メインゲーム
# =========================================
def main_game(active_lanes):

    score = 0

    notes = []

    count = {
        "PERFECT":0,
        "GOOD":0,
        "MISS":0
    }

    last_judge = None
    judge_timer = 0

    takuma_timer = 0
    nakayama_timer = 0

    TAKUMA_DISPLAY_TIME = 45
    NAKAYAMA_DISPLAY_TIME = 45

    JUDGE_DISPLAY_TIME = 30

    spawn_timer = 0

    next_spawn = random.randint(
        SPAWN_MIN,
        SPAWN_MAX
    )

    inactive_lanes = [
        l for l in LANES
        if l not in active_lanes
    ]

    # =====================================
    # BGM
    # =====================================
    pygame.mixer.music.load("source/rsc/bgm.mp3")

    pygame.mixer.music.set_volume(0.5)

    pygame.mixer.music.play()

    # =====================================
    # 効果音
    # =====================================
    se_perfect = pygame.mixer.Sound("source/rsc/Power.mp3")
    se_perfect.set_volume(1.0)

    se_miss = pygame.mixer.Sound("source/rsc/miss.mp3")
    se_miss.set_volume(1.0)

    # =====================================
    # 筋電値
    # =====================================
    left_arm = 0
    right_arm = 0
    left_chest = 0
    right_chest = 0

    can_input = True

    last_input_time = 0

    INPUT_COOLDOWN = 0.2

    last_read_time = 0

    READ_INTERVAL = 0.01

    while True:

        clock.tick(FPS)

        screen.fill((0,0,0))

        draw_lanes(active_lanes)

        # =================================
        # タイトル
        # =================================
        title = title_font.render(
            "MMC RHYTHM GAME",
            True,
            (255,100,255)
        )

        screen.blit(title, (20,15))

        # =================================
        # 判定BOX
        # =================================
        def draw_box(text, value, y, color):

            label = font.render(
                f"{text} × {value}",
                True,
                color
            )

            rect = label.get_rect(topleft=(20, y))

            pygame.draw.rect(
                screen,
                color,
                rect.inflate(12,8),
                2
            )

            screen.blit(label, rect)

        draw_box(
            "PERFECT",
            count["PERFECT"],
            70,
            (255,255,0)
        )

        draw_box(
            "GOOD",
            count["GOOD"],
            110,
            (0,255,0)
        )

        draw_box(
            "MISS",
            count["MISS"],
            150,
            (255,80,80)
        )

        # =================================
        # スコア
        # =================================
        score_text = font.render(
            f"TOTAL SCORE : {score}",
            True,
            (255,255,255)
        )

        screen.blit(
            score_text,
            (20, SCREEN_H - 60)
        )

        # =================================
        # body
        # =================================
        screen.blit(
            body_img,
            body_img.get_rect(
                center=(
                    SCREEN_W//2 + BODY_X_OFFSET,
                    SCREEN_H//2 + BODY_Y_OFFSET
                )
            )
        )

        # =================================
        # 筋電値表示
        # =================================
        emg1 = font.render(
            f"LEFT ARM : {left_arm}",
            True,
            (255,255,255)
        )

        emg2 = font.render(
            f"RIGHT ARM : {right_arm}",
            True,
            (255,255,255)
        )

        emg3 = font.render(
            f"LEFT CHEST : {left_chest}",
            True,
            (255,255,255)
        )

        emg4 = font.render(
            f"RIGHT CHEST : {right_chest}",
            True,
            (255,255,255)
        )

        screen.blit(emg1, (20, 220))
        screen.blit(emg2, (20, 250))
        screen.blit(emg3, (20, 280))
        screen.blit(emg4, (20, 310))

        # =================================
        # 固定筋肉
        # =================================
        for lane in inactive_lanes:

            img = muscle_imgs[lane]

            x, y = LANES[lane]

            screen.blit(
                img,
                img.get_rect(
                    center=(x + LANE_OFFSET_X, y)
                )
            )

        # =================================
        # 終了処理
        # =================================
        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                ser_arm.close()
                ser_chest.close()

                pygame.quit()
                sys.exit()

        # =================================
        # 筋電入力
        # =================================
        pressed_lane = None

        current_time = time.time()

        if current_time - last_read_time >= READ_INTERVAL:

            try:

                ser_arm.reset_input_buffer()
                ser_chest.reset_input_buffer()

                arm_data = ser_arm.readline().decode().strip().split(",")

                chest_data = ser_chest.readline().decode().strip().split(",")

                if len(arm_data) >= 2 and len(chest_data) >= 2:

                    left_arm = int(arm_data[0])
                    right_arm = int(arm_data[1])

                    left_chest = int(chest_data[0])
                    right_chest = int(chest_data[1])

                    last_read_time = current_time

                    if (
                        left_arm < THRESHOLD - 100 and
                        right_arm < THRESHOLD - 100 and
                        left_chest < THRESHOLD - 100 and
                        right_chest < THRESHOLD - 100
                    ):
                        can_input = True

                    if current_time - last_input_time > INPUT_COOLDOWN:

                        if can_input:

                            if left_arm > THRESHOLD:
                                pressed_lane = "left_arm"

                            elif right_arm > THRESHOLD:
                                pressed_lane = "right_arm"

                            elif left_chest > THRESHOLD:
                                pressed_lane = "left_chest"

                            elif right_chest > THRESHOLD:
                                pressed_lane = "right_chest"

                            if pressed_lane:

                                can_input = False

                                last_input_time = current_time

                                hit = False

                                for note in notes:

                                    if (
                                        note.lane == pressed_lane
                                        and note.active
                                    ):

                                        result = note.judge()

                                        if result:

                                            note.active = False

                                            count[result] += 1

                                            if result == "PERFECT":

                                                score += 300

                                                se_perfect.play()

                                                nakayama_timer = NAKAYAMA_DISPLAY_TIME

                                            else:

                                                score += 150

                                            last_judge = result

                                            judge_timer = JUDGE_DISPLAY_TIME

                                            hit = True

                                            break

                                if not hit:

                                    count["MISS"] += 1

                                    score -= 150

                                    se_miss.play()

                                    takuma_timer = TAKUMA_DISPLAY_TIME

                                    last_judge = "MISS"

                                    judge_timer = JUDGE_DISPLAY_TIME

            except:
                pass

        # =================================
        # ノーツ生成
        # =================================
        spawn_timer += 1

        if spawn_timer >= next_spawn:

            lane = random.choice(active_lanes)

            notes.append(Note(lane))

            spawn_timer = 0

            next_spawn = random.randint(
                SPAWN_MIN,
                SPAWN_MAX
            )

        # =================================
        # ノーツ更新
        # =================================
        for note in notes:

            result = note.update()

            if result == "MISS":

                count["MISS"] += 1

                score -= 150

                se_miss.play()

                takuma_timer = TAKUMA_DISPLAY_TIME

                last_judge = "MISS"

                judge_timer = JUDGE_DISPLAY_TIME

            note.draw()

        notes = [n for n in notes if n.active]

        # =================================
        # 判定文字
        # =================================
        if judge_timer > 0 and last_judge:

            color_map = {
                "PERFECT": (255,255,0),
                "GOOD": (0,255,0),
                "MISS": (255,80,80)
            }

            text = big_font.render(
                last_judge,
                True,
                color_map[last_judge]
            )

            rect = text.get_rect(
                center=(300, SCREEN_H//5)
            )

            screen.blit(text, rect)

            judge_timer -= 1

        # =================================
        # TAKUMA画像
        # =================================
        if takuma_timer > 0:

            screen.blit(
                takuma_img,
                (200, 300)
            )

            takuma_timer -= 1

        # =================================
        # NAKAYAMA画像
        # =================================
        if nakayama_timer > 0:

            screen.blit(
                nakayama_img,
                (200, 300)
            )

            nakayama_timer -= 1

        pygame.display.flip()

# =========================================
# 実行
# =========================================
if __name__ == "__main__":

    selected = select_muscles()

    main_game(selected)