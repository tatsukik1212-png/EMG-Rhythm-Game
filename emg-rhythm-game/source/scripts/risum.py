
import pygame
import random
import sys
import serial
import time

# =====================
# 基本設定
# =====================
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

THRESHOLD = 700

# =====================
# レーン位置
# =====================
LANES = {
    "left_arm": (328, 345),
    "right_arm": (675, 345),
    "left_chest": (444, 410),
    "right_chest": (560, 405),
}

# =====================
# 筋肉名
# =====================
MUSCLE_NAMES = {
    "left_arm": "Left Arm",
    "right_arm": "Right Arm",
    "left_chest": "Left Chest",
    "right_chest": "Right Chest",
}

# =====================
# pygame初期化
# =====================
pygame.init()

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("MMC RHYTHM GAME")

clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 26)
big_font = pygame.font.SysFont(None, 44)
title_font = pygame.font.SysFont(None, 48)

# =====================
# Arduino接続
# =====================
try:
    ser_arm = serial.Serial("COM4", 115200)
    ser_chest = serial.Serial("COM5", 115200)

    time.sleep(2)

except Exception as e:
    print("Serial Error:", e)
    sys.exit()

last_input_time = 0
INPUT_COOLDOWN = 0.2

# =====================
# 画像読み込み
# =====================
def load_img(path, size=None):

    img = pygame.image.load(path).convert_alpha()

    if size:
        img = pygame.transform.smoothscale(img, size)

    return img


body_img = load_img("images/body.png", BODY_SIZE)

muscle_imgs = {
    "left_arm": load_img("images/left_arm.png", ARM_NOTE_SIZE),
    "right_arm": load_img("images/right_arm.png", ARM_NOTE_SIZE),
    "left_chest": load_img("images/left_chest.png", CHEST_NOTE_SIZE),
    "right_chest": load_img("images/right_chest.png", CHEST_NOTE_SIZE),
}

# =====================
# レーン描画
# =====================
def draw_lanes():

    for _, (x, y) in LANES.items():

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

# =====================
# ノーツ
# =====================
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

        screen.blit(
            img,
            img.get_rect(center=(self.x, self.y))
        )

    def judge(self):

        diff = abs(self.y - self.hit_y)

        if diff <= PERFECT_RANGE:
            return "PERFECT"

        elif diff <= GOOD_RANGE:
            return "GOOD"

        return None

# =====================
# 筋肉選択画面
# =====================
def select_muscles():

    selected = []

    while True:

        screen.fill((0, 0, 0))

        title = big_font.render(
            "Select 2 Muscles",
            True,
            (255, 255, 255)
        )

        screen.blit(
            title,
            (SCREEN_W // 2 - title.get_width() // 2, 40)
        )

        for i, key in enumerate(MUSCLE_NAMES):

            x = 250 + (i % 2) * 350
            y = 180 + (i // 2) * 220

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
                    rect.inflate(14, 14),
                    3
                )

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:

                mx, my = event.pos

                for i, key in enumerate(MUSCLE_NAMES):

                    x = 250 + (i % 2) * 350
                    y = 180 + (i // 2) * 220

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

# =====================
# メインゲーム
# =====================
def main_game(active_lanes):

    global last_input_time

    score = 0

    notes = []

    count = {
        "PERFECT": 0,
        "GOOD": 0,
        "MISS": 0
    }

    last_judge = None
    judge_timer = 0
    JUDGE_DISPLAY_TIME = 30

    spawn_timer = 0
    next_spawn = random.randint(SPAWN_MIN, SPAWN_MAX)

    inactive_lanes = [
        l for l in LANES
        if l not in active_lanes
    ]

    # =====================
    # 筋電初期値
    # =====================
    left_arm = 0
    right_arm = 0
    left_chest = 0
    right_chest = 0

    can_input = True

    last_read_time = 0
    READ_INTERVAL = 0.01

    while True:

        clock.tick(FPS)

        screen.fill((0, 0, 0))

        draw_lanes()

        # =====================
        # タイトル
        # =====================
        title = title_font.render(
            "MMC RHYTHM GAME",
            True,
            (255, 100, 255)
        )

        screen.blit(title, (20, 15))

        # =====================
        # 判定数表示
        # =====================
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
                rect.inflate(12, 8),
                2
            )

            screen.blit(label, rect)

        draw_box("PERFECT", count["PERFECT"], 70, (255, 255, 0))
        draw_box("GOOD", count["GOOD"], 110, (0, 255, 0))
        draw_box("MISS", count["MISS"], 150, (255, 80, 80))

        # =====================
        # スコア
        # =====================
        score_text = font.render(
            f"TOTAL SCORE : {score}",
            True,
            (255, 255, 255)
        )

        screen.blit(score_text, (20, SCREEN_H - 60))

        # =====================
        # body表示
        # =====================
        screen.blit(
            body_img,
            body_img.get_rect(
                center=(
                    SCREEN_W // 2 + BODY_X_OFFSET,
                    SCREEN_H // 2 + BODY_Y_OFFSET
                )
            )
        )

        # =====================
        # 筋電値表示
        # =====================
        emg1 = font.render(
            f"LEFT ARM : {left_arm}",
            True,
            (255, 255, 255)
        )

        emg2 = font.render(
            f"RIGHT ARM : {right_arm}",
            True,
            (255, 255, 255)
        )

        emg3 = font.render(
            f"LEFT CHEST : {left_chest}",
            True,
            (255, 255, 255)
        )

        emg4 = font.render(
            f"RIGHT CHEST : {right_chest}",
            True,
            (255, 255, 255)
        )

        screen.blit(emg1, (20, 220))
        screen.blit(emg2, (20, 250))
        screen.blit(emg3, (20, 280))
        screen.blit(emg4, (20, 310))

        # =====================
        # 固定筋肉表示
        # =====================
        for lane in inactive_lanes:

            img = muscle_imgs[lane]

            x, y = LANES[lane]

            screen.blit(
                img,
                img.get_rect(center=(x + LANE_OFFSET_X, y))
            )

        # =====================
        # 終了処理
        # =====================
        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                ser_arm.close()
                ser_chest.close()

                pygame.quit()
                sys.exit()

        # =====================
        # 筋電入力
        # =====================
        pressed_lane = None

        current_time = time.time()

        if current_time - last_read_time >= READ_INTERVAL:

            try:

                arm_data = [0,0] #ser_arm.readline().decode().strip().split(",")
                chest_data = ser_chest.readline().decode().strip().split(",")

                if len(arm_data) >= 2 and len(chest_data) >= 2:

                    left_arm = int(arm_data[0])
                    right_arm = int(arm_data[1])

                    left_chest = int(chest_data[0])
                    right_chest = int(chest_data[1])

                    last_read_time = current_time

                    # 力み解除
                    if (
                        left_arm < THRESHOLD - 100 and
                        right_arm < THRESHOLD - 100 and
                        left_chest < THRESHOLD - 100 and
                        right_chest < THRESHOLD - 100
                    ):
                        can_input = True

                    # 入力判定
                    if current_time - last_input_time > INPUT_COOLDOWN:

                        if left_arm > THRESHOLD and can_input:
                            pressed_lane = "left_arm"

                        elif right_arm > THRESHOLD and can_input:
                            pressed_lane = "right_arm"

                        elif left_chest > THRESHOLD and can_input:
                            pressed_lane = "left_chest"

                        elif right_chest > THRESHOLD and can_input:
                            pressed_lane = "right_chest"

                        if pressed_lane:

                            can_input = False
                            last_input_time = current_time

            except Exception as e:
                print(e)

        # =====================
        # ノーツ判定
        # =====================
        if pressed_lane:

            hit = False

            for note in notes:

                if note.lane == pressed_lane and note.active:

                    result = note.judge()

                    if result:

                        note.active = False

                        count[result] += 1

                        if result == "PERFECT":
                            score += 300
                        else:
                            score += 150

                        last_judge = result
                        judge_timer = JUDGE_DISPLAY_TIME

                        hit = True

                        break

            if not hit:

                count["MISS"] += 1
                score -= 150

                last_judge = "MISS"
                judge_timer = JUDGE_DISPLAY_TIME

        # =====================
        # ノーツ生成
        # =====================
        spawn_timer += 1

        if spawn_timer >= next_spawn:

            notes.append(
                Note(random.choice(active_lanes))
            )

            spawn_timer = 0

            next_spawn = random.randint(
                SPAWN_MIN,
                SPAWN_MAX
            )

        # =====================
        # ノーツ更新
        # =====================
        for note in notes:

            miss_result = note.update()

            note.draw()

            if miss_result == "MISS":

                count["MISS"] += 1
                score -= 100

                last_judge = "MISS"
                judge_timer = JUDGE_DISPLAY_TIME

        notes = [n for n in notes if n.active]

        # =====================
        # 判定表示
        # =====================
        if judge_timer > 0 and last_judge:

            color_map = {
                "PERFECT": (255, 255, 0),
                "GOOD": (0, 255, 0),
                "MISS": (255, 80, 80)
            }

            text = big_font.render(
                last_judge,
                True,
                color_map[last_judge]
            )

            rect = text.get_rect(
                center=(200, SCREEN_H // 2)
            )

            screen.blit(text, rect)

            judge_timer -= 1

        pygame.display.flip()

# =====================
# 実行
# =====================
if __name__ == "__main__":

    selected = select_muscles()

    main_game(selected)
