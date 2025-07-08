import pygame
import sys
import random
import time
import os
import numpy

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PADDLE_WIDTH = 10
PADDLE_HEIGHT = 100
BALL_SIZE = 20
PADDLE_SPEED = 7
BALL_SPEED_X = 6
BALL_SPEED_Y = 6
WINNING_SCORE = 10
SPLASH_TIME = 5  # seconds

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Pong')
clock = pygame.time.Clock()
font_large = pygame.font.SysFont(None, 100)
font_medium = pygame.font.SysFont(None, 60)
font_small = pygame.font.SysFont(None, 40)

# Config file path
CONFIG_FILE = 'config.py'

# Default settings
DEFAULT_SETTINGS = {
    'WINNING_SCORE': 10,
    'AI_DIFFICULTY': 'Normal',  # Options: 'Easy', 'Normal', 'Hard'
}

# AI difficulty mapping
AI_DIFFICULTY_MAP = {
    'Easy': 0.15,   # 15% miss
    'Normal': 0.05, # 5% miss
    'Hard': 0.01,   # 1% miss
    'Extreme': 0.001, # 0.1% miss
}

# Sound
pygame.mixer.init()
try:
    PADDLE_SOUND = pygame.mixer.Sound('paddle.wav')
except Exception:
    # Generate a simple beep sound if paddle.wav is not found
    frequency = 440  # Hz
    duration = 0.05  # seconds
    sample_rate = 44100
    t = numpy.linspace(0, duration, int(sample_rate * duration), False)
    tone = numpy.sin(frequency * 2 * numpy.pi * t) * 0.5
    audio = numpy.array(tone * 32767, dtype=numpy.int16)
    PADDLE_SOUND = pygame.mixer.Sound(buffer=audio.tobytes())

# Missed ball sound (different beep)
def get_miss_sound():
    frequency = 220  # Hz (lower pitch)
    duration = 0.05  # seconds
    sample_rate = 44100
    t = numpy.linspace(0, duration, int(sample_rate * duration), False)
    tone = numpy.sin(frequency * 2 * numpy.pi * t) * 0.5
    audio = numpy.array(tone * 32767, dtype=numpy.int16)
    return pygame.mixer.Sound(buffer=audio.tobytes())

MISS_SOUND = get_miss_sound()

def draw_text(text, font, color, surface, x, y, center=True):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    if center:
        textrect.center = (x, y)
    else:
        textrect.topleft = (x, y)
    surface.blit(textobj, textrect)


def splash_screen():
    screen.fill(BLACK)
    draw_text('An Adam Production', font_large, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    pygame.display.flip()
    start_time = time.time()
    while time.time() - start_time < SPLASH_TIME:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        clock.tick(60)


def load_settings():
    if os.path.exists(CONFIG_FILE):
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location('config', CONFIG_FILE)
            if spec is not None and spec.loader is not None:
                config = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(config)
                return {
                    'WINNING_SCORE': getattr(config, 'WINNING_SCORE', DEFAULT_SETTINGS['WINNING_SCORE']),
                    'AI_DIFFICULTY': getattr(config, 'AI_DIFFICULTY', DEFAULT_SETTINGS['AI_DIFFICULTY']),
                }
            else:
                return DEFAULT_SETTINGS.copy()
        except Exception:
            return DEFAULT_SETTINGS.copy()
    else:
        return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    with open(CONFIG_FILE, 'w') as f:
        f.write(f"WINNING_SCORE = {settings['WINNING_SCORE']}\n")
        f.write(f"AI_DIFFICULTY = '{settings['AI_DIFFICULTY']}'\n")

settings = load_settings()


def title_screen():
    options = ['Start', 'Settings', 'Exit']
    selected = 0
    waiting = True
    while waiting:
        screen.fill(BLACK)
        draw_text('Pong', font_large, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100)
        for i, option in enumerate(options):
            color = WHITE if i == selected else GRAY
            draw_text(option, font_small, color, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20 + i * 50)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    if options[selected] == 'Start':
                        return 'start'
                    elif options[selected] == 'Settings':
                        return 'settings'
                    elif options[selected] == 'Exit':
                        pygame.quit()
                        sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for i, option in enumerate(options):
                    text_surface = font_small.render(option, True, WHITE)
                    text_rect = text_surface.get_rect()
                    text_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20 + i * 50)
                    if text_rect.collidepoint(mouse_pos):
                        if options[i] == 'Start':
                            return 'start'
                        elif options[i] == 'Settings':
                            return 'settings'
                        elif options[i] == 'Exit':
                            pygame.quit()
                            sys.exit()
        clock.tick(60)


def settings_screen():
    global settings
    options = ['Points to Win', 'AI Difficulty', 'Back']
    selected = 0
    ai_difficulties = list(AI_DIFFICULTY_MAP.keys())
    ai_selected = ai_difficulties.index(settings['AI_DIFFICULTY']) if settings['AI_DIFFICULTY'] in ai_difficulties else 1
    points = settings['WINNING_SCORE']
    editing = False
    while True:
        screen.fill(BLACK)
        draw_text('Settings', font_large, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 120)
        for i, option in enumerate(options):
            color = WHITE if i == selected else GRAY
            if option == 'Points to Win':
                text = f"{option}: {points}"
            elif option == 'AI Difficulty':
                text = f"{option}: {ai_difficulties[ai_selected]}"
            else:
                text = option
            draw_text(text, font_small, color, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10 + i * 50)
        draw_text('Use arrows to change, Enter to select', font_small, GRAY, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                if selected == 0 and (event.key == pygame.K_LEFT or event.key == pygame.K_MINUS):
                    points = max(1, points - 1)
                if selected == 0 and (event.key == pygame.K_RIGHT or event.key == pygame.K_PLUS):
                    points = min(99, points + 1)
                if selected == 1 and event.key == pygame.K_LEFT:
                    ai_selected = (ai_selected - 1) % len(ai_difficulties)
                if selected == 1 and event.key == pygame.K_RIGHT:
                    ai_selected = (ai_selected + 1) % len(ai_difficulties)
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if options[selected] == 'Back':
                        # Save settings
                        settings['WINNING_SCORE'] = points
                        settings['AI_DIFFICULTY'] = ai_difficulties[ai_selected]
                        save_settings(settings)
                        return
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for i, option in enumerate(options):
                    if option == 'Points to Win':
                        text = f"{option}: {points}"
                    elif option == 'AI Difficulty':
                        text = f"{option}: {ai_difficulties[ai_selected]}"
                    else:
                        text = option
                    text_surface = font_small.render(text, True, WHITE)
                    text_rect = text_surface.get_rect()
                    text_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10 + i * 50)
                    if text_rect.collidepoint(mouse_pos):
                        if options[i] == 'Back':
                            # Save settings
                            settings['WINNING_SCORE'] = points
                            settings['AI_DIFFICULTY'] = ai_difficulties[ai_selected]
                            save_settings(settings)
                            return
        clock.tick(60)


def end_screen(winner):
    waiting = True
    while waiting:
        screen.fill(BLACK)
        draw_text(f'{winner} Wins!', font_large, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40)
        draw_text('Press SPACE to continue', font_small, GRAY, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False
        clock.tick(60)


def reset_ball(ball_rect, direction):
    ball_rect.x = SCREEN_WIDTH // 2 - BALL_SIZE // 2
    ball_rect.y = SCREEN_HEIGHT // 2 - BALL_SIZE // 2
    ball_speed_x = BALL_SPEED_X * direction
    ball_speed_y = BALL_SPEED_Y * random.choice([-1, 1])
    return ball_speed_x, ball_speed_y


def main_game():
    # Paddles
    player_rect = pygame.Rect(30, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    ai_rect = pygame.Rect(SCREEN_WIDTH - 40, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    # Ball
    ball_rect = pygame.Rect(SCREEN_WIDTH // 2 - BALL_SIZE // 2, SCREEN_HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)
    ball_speed_x = BALL_SPEED_X * random.choice([-1, 1])
    ball_speed_y = BALL_SPEED_Y * random.choice([-1, 1])
    # Scores
    player_score = 0
    ai_score = 0
    # AI miss chance
    ai_miss = False
    ai_miss_timer = 0
    ai_miss_chance = AI_DIFFICULTY_MAP.get(settings['AI_DIFFICULTY'], 0.05)
    # Ball speed multiplier
    speed_multiplier = 1.0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and player_rect.top > 0:
            player_rect.y -= PADDLE_SPEED
        if keys[pygame.K_DOWN] and player_rect.bottom < SCREEN_HEIGHT:
            player_rect.y += PADDLE_SPEED

        # AI movement
        if ball_speed_x > 0 and random.random() < ai_miss_chance and not ai_miss and abs(ball_rect.centery - ai_rect.centery) < 100:
            ai_miss = True
            ai_miss_timer = random.randint(20, 40)  # frames to miss
        if ai_miss:
            ai_miss_timer -= 1
            if ai_miss_timer <= 0:
                ai_miss = False
        if not ai_miss:
            if ai_rect.centery < ball_rect.centery and ai_rect.bottom < SCREEN_HEIGHT:
                ai_rect.y += PADDLE_SPEED
            elif ai_rect.centery > ball_rect.centery and ai_rect.top > 0:
                ai_rect.y -= PADDLE_SPEED
        else:
            pass

        # Ball movement
        ball_rect.x += int(ball_speed_x * speed_multiplier)
        ball_rect.y += int(ball_speed_y * speed_multiplier)

        # Collisions with top/bottom
        if ball_rect.top <= 0 or ball_rect.bottom >= SCREEN_HEIGHT:
            ball_speed_y *= -1

        # Collisions with paddles
        hit_paddle = False
        if ball_rect.colliderect(player_rect):
            if ball_speed_x < 0:
                ball_speed_x *= -1
                ball_speed_y += random.randint(-2, 2)
                hit_paddle = True
        if ball_rect.colliderect(ai_rect):
            if ball_speed_x > 0:
                ball_speed_x *= -1
                ball_speed_y += random.randint(-2, 2)
                hit_paddle = True
        if hit_paddle:
            speed_multiplier *= 1.05  # Increase speed by 5%
            if PADDLE_SOUND:
                PADDLE_SOUND.play()

        # Score update
        if ball_rect.left <= 0:
            ai_score += 1
            ball_speed_x, ball_speed_y = reset_ball(ball_rect, direction=1)
            ai_miss = False
            speed_multiplier = 1.0
            for _ in range(3):
                if MISS_SOUND:
                    MISS_SOUND.play()
                pygame.time.wait(60)
            time.sleep(0.5)
        if ball_rect.right >= SCREEN_WIDTH:
            player_score += 1
            ball_speed_x, ball_speed_y = reset_ball(ball_rect, direction=-1)
            ai_miss = False
            speed_multiplier = 1.0
            for _ in range(3):
                if MISS_SOUND:
                    MISS_SOUND.play()
                pygame.time.wait(60)
            time.sleep(0.5)

        # Draw everything
        screen.fill(BLACK)
        pygame.draw.rect(screen, WHITE, player_rect)
        pygame.draw.rect(screen, WHITE, ai_rect)
        pygame.draw.ellipse(screen, WHITE, ball_rect)
        pygame.draw.aaline(screen, WHITE, (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT))
        draw_text(str(player_score), font_medium, WHITE, screen, SCREEN_WIDTH // 4, 40)
        draw_text(str(ai_score), font_medium, WHITE, screen, SCREEN_WIDTH * 3 // 4, 40)
        pygame.display.flip()
        clock.tick(60)

        # Check for winner
        if player_score >= settings['WINNING_SCORE']:
            return 'Player'
        if ai_score >= settings['WINNING_SCORE']:
            return 'AI'


def main():
    while True:
        splash_screen()
        while True:
            action = title_screen()
            if action == 'start':
                winner = main_game()
                end_screen(winner)
            elif action == 'settings':
                settings_screen()


if __name__ == '__main__':
    main()
