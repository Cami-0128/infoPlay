# 貪吃蛇
import pygame
import random
import sys
import os

pygame.init()

# 嘗試載入中文字型
font_path = None
possible_fonts = ["msjh.ttc", "msjh.ttf", "mingliu.ttc", "simhei.ttf", "Microsoft JhengHei.ttf"]
windows_font_dir = os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts")
for fname in possible_fonts:
    fpath = os.path.join(windows_font_dir, fname)
    if os.path.exists(fpath):
        font_path = fpath
        break
if font_path is None:
    print("找不到中文字型，請安裝或加入字型檔。")
    sys.exit()

# 遊戲設定
WIDTH, HEIGHT = 600, 400
CELL_SIZE = 20
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("貪吃蛇進階版")
clock = pygame.time.Clock()
FPS = 10

# 顏色設定
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (200, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
SNAKE_GREEN = (0, 180, 0)

# 遊戲狀態變數
font = pygame.font.Font(font_path, 24)
snake = [(100, 100), (80, 100), (60, 100)]
direction = (CELL_SIZE, 0)
score = 0
high_score = 0
deaths = 0
lives = 0
foods = []
bombs = []

# 生成功能
def spawn_food():
    for _ in range(2):
        x = random.randrange(0, WIDTH, CELL_SIZE)
        y = random.randrange(0, HEIGHT, CELL_SIZE)
        foods.append({"pos": (x, y), "type": "score"})
    if random.random() < 0.2:
        x = random.randrange(0, WIDTH, CELL_SIZE)
        y = random.randrange(0, HEIGHT, CELL_SIZE)
        foods.append({"pos": (x, y), "type": "shield"})

def spawn_bomb():
    x = random.randrange(0, WIDTH, CELL_SIZE)
    y = random.randrange(0, HEIGHT, CELL_SIZE)
    bombs.append({"pos": (x, y), "timer": FPS * 4})

# 繪圖功能
def draw_snake():
    for segment in snake:
        pygame.draw.rect(screen, SNAKE_GREEN, (*segment, CELL_SIZE, CELL_SIZE))

def draw_foods():
    for food in foods:
        color = YELLOW if food["type"] == "score" else BLUE
        pygame.draw.rect(screen, color, (*food["pos"], CELL_SIZE, CELL_SIZE))

def draw_bombs():
    for bomb in bombs:
        pygame.draw.rect(screen, RED, (*bomb["pos"], CELL_SIZE, CELL_SIZE))

def draw_score():
    text = font.render(f"分數: {score}  最高分: {high_score}  死亡: {deaths}  護身符: {lives}", True, WHITE)
    screen.blit(text, (10, 10))

# 碰撞判斷
def handle_collision():
    global score, lives, foods, bombs, snake
    head = snake[0]

    for i, food in enumerate(foods):
        if head == food["pos"]:
            if food["type"] == "score":
                score += 1
                snake.append(snake[-1])
            elif food["type"] == "shield":
                lives += 1
            del foods[i]
            break

    for bomb in bombs:
        if head == bomb["pos"]:
            if lives > 0:
                lives -= 1
                bombs.remove(bomb)
                return False
            else:
                return True
    return False

# 撞牆時自動轉向
def avoid_wall_with_life():
    global direction
    head = snake[0]
    dx, dy = direction
    next_x = head[0] + dx
    next_y = head[1] + dy

    if (next_x < 0 or next_x >= WIDTH or next_y < 0 or next_y >= HEIGHT):
        alternatives = [(CELL_SIZE, 0), (-CELL_SIZE, 0), (0, CELL_SIZE), (0, -CELL_SIZE)]
        for new_dir in alternatives:
            if new_dir == (-dx, -dy):
                continue
            new_x = head[0] + new_dir[0]
            new_y = head[1] + new_dir[1]
            if 0 <= new_x < WIDTH and 0 <= new_y < HEIGHT and (new_x, new_y) not in snake:
                direction = new_dir
                break

# 死亡畫面與選單
def game_over():
    global snake, direction, score, high_score, deaths, lives, foods, bombs
    deaths += 1
    high_score = max(high_score, score)

    screen.fill(BLACK)
    msg1 = font.render("你死了！按 Enter 繼續，ESC 離開", True, YELLOW)
    screen.blit(msg1, (WIDTH//2 - 140, HEIGHT//2 - 20))

    if deaths > 1:
        msg2 = font.render(f"總死亡次數: {deaths}  最高分: {high_score}", True, WHITE)
        screen.blit(msg2, (WIDTH//2 - 130, HEIGHT//2 + 20))

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    snake[:] = [(100, 100), (80, 100), (60, 100)]
                    direction = (CELL_SIZE, 0)
                    score = 0
                    lives = 0
                    foods.clear()
                    bombs.clear()
                    spawn_food()
                    return
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

# 初始生成食物
spawn_food()

# ===== 主遊戲迴圈 =====
while True:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and direction != (0, CELL_SIZE):
                direction = (0, -CELL_SIZE)
            elif event.key == pygame.K_DOWN and direction != (0, -CELL_SIZE):
                direction = (0, CELL_SIZE)
            elif event.key == pygame.K_LEFT and direction != (CELL_SIZE, 0):
                direction = (-CELL_SIZE, 0)
            elif event.key == pygame.K_RIGHT and direction != (-CELL_SIZE, 0):
                direction = (CELL_SIZE, 0)

    # 預測下一步
    next_head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
    dead = False

    if (next_head[0] < 0 or next_head[0] >= WIDTH or
        next_head[1] < 0 or next_head[1] >= HEIGHT or
        next_head in snake):
        
        if lives > 0:
            lives -= 1
            avoid_wall_with_life()
            dx, dy = direction
            next_head = (snake[0][0] + dx, snake[0][1] + dy)
            if (next_head[0] < 0 or next_head[0] >= WIDTH or
                next_head[1] < 0 or next_head[1] >= HEIGHT or
                next_head in snake):
                dead = True
        else:
            dead = True

    if not dead:
        snake.insert(0, next_head)
        snake.pop()

    if not dead and handle_collision():
        dead = True

    # 死亡畫面延遲兩秒
    if dead:
        screen.fill(BLACK)
        draw_snake()
        draw_foods()
        draw_bombs()
        draw_score()
        pygame.display.flip()
        pygame.time.delay(2000)
        game_over()
        continue

    for bomb in bombs[:]:
        bomb["timer"] -= 1
        if bomb["timer"] <= 0:
            bombs.remove(bomb)

    if len(foods) < 3:
        spawn_food()
    if random.random() < 0.02:
        spawn_bomb()

    draw_snake()
    draw_foods()
    draw_bombs()
    draw_score()
    pygame.display.flip()
    clock.tick(FPS)