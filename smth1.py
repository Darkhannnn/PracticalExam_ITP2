import pygame
import sys
import random
import os

pygame.init()

WIDTH, HEIGHT = 2560//2, 1600//2
PLAYER_SIZE = 33
BLOCK_SIZE = 81
COIN_SIZE = 20

BULLET_WIDTH = 4
BULLET_HEIGHT = 10
SHOOT_DELAY = 1

ENEMY_INITIAL_SPEED = 2
ENEMY_SPEED = ENEMY_INITIAL_SPEED

FPS = 60

WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dodge the Blocks")

clock = pygame.time.Clock()

main_dir = os.path.split(os.path.abspath(__file__))[0]
if pygame.mixer:
    music = os.path.join(main_dir, "data", "song.mp3")
    pygame.mixer.music.load(music)
    pygame.mixer.music.play(-1)

def load_image(file):
    file = os.path.join(main_dir, "data", file)
    try:
        surface = pygame.image.load(file)
    except pygame.error:
        raise SystemExit(f'Could not load image "{file}" {pygame.get_error()}')
    return surface.convert()

def load_sound(file):
    if not pygame.mixer:
        return None
    file = os.path.join(main_dir, "data", file)
    try:
        sound = pygame.mixer.Sound(file)
        return sound
    except pygame.error:
        print(f"Warning, unable to load, {file}")
    return None

player_images = {
    "up": load_image("player_up.png"),
    "down": load_image("player_down.png"),
    "left": load_image("player_left.png"),
    "right": load_image("player_right.png")
}
current_direction = "left"

coin_image = load_image("coin.png")

block_images = [
    load_image("enemy1.png"),
    load_image("enemy2.png"),
    load_image("enemy3.png"),
    load_image("enemy4.png")
]

player = pygame.Rect(WIDTH // 2 - PLAYER_SIZE // 2, HEIGHT - PLAYER_SIZE - 10, PLAYER_SIZE, PLAYER_SIZE)

blocks = []
coins = []
bullets = []

score = 0
coin_score = 0
font = pygame.font.Font(None, 36)

game_active = False
last_shot_time = pygame.time.get_ticks()

def draw_player():
    screen.blit(player_images[current_direction], player)

def update_player_direction():
    global current_direction
    if keys[pygame.K_LEFT] and player.x > 0:
        current_direction = "left"
    elif keys[pygame.K_RIGHT] and player.x < WIDTH - PLAYER_SIZE:
        current_direction = "right"
    elif keys[pygame.K_UP] and player.y > 0:
        current_direction = "up"
    elif keys[pygame.K_DOWN] and player.y < HEIGHT - PLAYER_SIZE:
        current_direction = "down"


def generate_block():
    if random.randint(0, 100) < 5:
        block_type = random.randint(0, 3)  # Randomly choose one of the four block types
        block = [pygame.Rect(random.randint(0, WIDTH - BLOCK_SIZE), 0, BLOCK_SIZE, BLOCK_SIZE), block_type]
        blocks.append(block)

def draw_blocks():
    for block in blocks:
        screen.blit(block_images[block[1]], block[0])

def move_blocks():
    for block in blocks:
        block[0].y += ENEMY_SPEED
        if block[0].y > HEIGHT:
            blocks.remove(block)
            global score
            score += 1


def generate_coin():
    if random.randint(0, 100) < 5:
        coin = pygame.Rect(random.randint(0, WIDTH - COIN_SIZE), 0, COIN_SIZE, COIN_SIZE)
        if not any(coin.colliderect(block[0]) for block in blocks) and not any(coin.colliderect(existing_coin) for existing_coin in coins):
            coins.append(coin)

def draw_coins():
    for coin in coins:
        screen.blit(coin_image, coin)

def move_coins():
    for coin in coins:
        coin.y += 2
        if coin.y > HEIGHT:
            coins.remove(coin)

def check_coin_collection():
    global coin_score
    for coin in coins[:]:
        if player.colliderect(coin):
            coins.remove(coin)
            coin_score += 1


def draw_bullets():
    for bullet in bullets:
        pygame.draw.rect(screen, WHITE, bullet)

def move_bullets():
    for bullet in bullets:
        bullet.y -= 5
        if bullet.y < 0:
            bullets.remove(bullet)

def check_bullet_collision():
    global score
    for bullet in bullets[:]:
        for block in blocks[:]:
            block_rect = block[0]
            if bullet.colliderect(block_rect):
                bullets.remove(bullet)
                blocks.remove(block)
                score += 2


def display_score():
    score_text = font.render("Score: " + str(score), True, WHITE)
    screen.blit(score_text, (10, 10))

def display_coin_score():
    coin_score_text = font.render("Coins: " + str(coin_score), True, WHITE)
    screen.blit(coin_score_text, (10, 40))


def show_start_menu():
    font_start = pygame.font.Font(None, 48)
    text_start = font_start.render("Hello! Press any key to start", True, WHITE)
    screen.blit(text_start, (WIDTH // 2 - 250, HEIGHT // 2 - 25))

def show_game_over():
    gameover_sound.play()
    # pygame.time.wait(1000)
    font_game_over = pygame.font.Font(None, 48)
    text_game_over = font_game_over.render("Game Over! Total score: " + str(score+coin_score*2), True, WHITE)
    screen.blit(text_game_over, (WIDTH // 2 - 250, HEIGHT // 2 - 25))
    pygame.display.flip()
    pygame.time.wait(2000)
    wait_for_key()

def wait_for_key():
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()

    if not game_active:
        screen.fill((0, 0, 0))
        show_start_menu()
        if any(keys):
            game_active = True
            player.y = HEIGHT - PLAYER_SIZE - 10
            ENEMY_SPEED = ENEMY_INITIAL_SPEED
    else:
        update_player_direction()

        if keys[pygame.K_LEFT] and player.x > 0:
            player.x -= 5
        if keys[pygame.K_RIGHT] and player.x < WIDTH - PLAYER_SIZE:
            player.x += 5
        if keys[pygame.K_UP] and player.y > 0:
            player.y -= 5
        if keys[pygame.K_DOWN] and player.y < HEIGHT - PLAYER_SIZE:
            player.y += 5
        if keys[pygame.K_SPACE] and pygame.time.get_ticks() - last_shot_time > SHOOT_DELAY * 1000:
            bullet = pygame.Rect(player.x + PLAYER_SIZE // 2 - BULLET_WIDTH // 2, player.y - BULLET_HEIGHT, BULLET_WIDTH, BULLET_HEIGHT)
            bullets.append(bullet)
            last_shot_time = pygame.time.get_ticks()

        if keys[pygame.K_q]:
            ENEMY_SPEED += 100

        gameover_sound = load_sound("dying.mp3")

        screen.fill((0, 0, 0))
        move_blocks()
        generate_block()
        move_coins()
        generate_coin()
        check_coin_collection()
        move_bullets()
        draw_bullets()
        check_bullet_collision()
        draw_player()
        draw_blocks()
        draw_coins()
        display_score()
        display_coin_score()

        for block in blocks:
            if player.colliderect(block[0]):
                game_active = False
                show_game_over()
                blocks.clear()
                coins.clear()
                score = 0
                coin_score = 0

        if score % 50 == 0 and score != 0:
            ENEMY_SPEED += 0.1

    pygame.display.flip()
    clock.tick(FPS)

