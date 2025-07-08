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

# Missile hit sound
def get_missile_sound():
    frequency = 880  # Hz (higher pitch)
    duration = 0.1  # seconds
    sample_rate = 44100
    t = numpy.linspace(0, duration, int(sample_rate * duration), False)
    tone = numpy.sin(frequency * 2 * numpy.pi * t) * 0.5
    audio = numpy.array(tone * 32767, dtype=numpy.int16)
    return pygame.mixer.Sound(buffer=audio.tobytes())

MISSILE_SOUND = get_missile_sound()

# Celebration sound
def get_celebration_sound():
    frequency = 660  # Hz (medium pitch)
    duration = 0.2  # seconds
    sample_rate = 44100
    t = numpy.linspace(0, duration, int(sample_rate * duration), False)
    tone = numpy.sin(frequency * 2 * numpy.pi * t) * 0.5
    audio = numpy.array(tone * 32767, dtype=numpy.int16)
    return pygame.mixer.Sound(buffer=audio.tobytes())

CELEBRATION_SOUND = get_celebration_sound()

# Countdown sound
def get_countdown_sound():
    frequency = 330  # Hz (lower pitch)
    duration = 0.1  # seconds
    sample_rate = 44100
    t = numpy.linspace(0, duration, int(sample_rate * duration), False)
    tone = numpy.sin(frequency * 2 * numpy.pi * t) * 0.5
    audio = numpy.array(tone * 32767, dtype=numpy.int16)
    return pygame.mixer.Sound(buffer=audio.tobytes())

COUNTDOWN_SOUND = get_countdown_sound()

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
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    selected = (selected - 1) % len(options)
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
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
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    selected = (selected - 1) % len(options)
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
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


def countdown():
    for i in range(3, 0, -1):
        screen.fill(BLACK)
        draw_text(str(i), font_large, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        pygame.display.flip()
        if COUNTDOWN_SOUND:
            COUNTDOWN_SOUND.play()
        pygame.time.wait(1000)
    screen.fill(BLACK)
    draw_text('GO!', font_large, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    pygame.display.flip()
    if COUNTDOWN_SOUND:
        COUNTDOWN_SOUND.play()
    pygame.time.wait(500)  # 0.5 seconds for "GO!"

def ball_countdown():
    for i in range(3, 0, -1):
        screen.fill(BLACK)
        draw_text(str(i), font_large, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        pygame.display.flip()
        if COUNTDOWN_SOUND:
            COUNTDOWN_SOUND.play()
        pygame.time.wait(1000)
    screen.fill(BLACK)
    draw_text('GO!', font_large, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    pygame.display.flip()
    if COUNTDOWN_SOUND:
        COUNTDOWN_SOUND.play()
    pygame.time.wait(1500)  # 1.5 seconds total (0.5 + 1.0)


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
    # Missiles
    missiles = []
    missile_speed = 8
    # Missile cooldowns
    player_missile_cooldown = 0
    ai_missile_cooldown = 0
    missile_cooldown_frames = 90  # 1.5 seconds at 60fps
    # Star power-ups
    star_rect = None
    star_type = None  # 'yellow', 'blue', 'green'
    star_spawn_timer = 0
    star_spawn_interval = 600  # 10 seconds at 60fps
    # Power-up timers
    player_tall_paddle_timer = 0
    player_fast_movement_timer = 0
    ai_tall_paddle_timer = 0
    ai_fast_movement_timer = 0
    power_up_duration = 300  # 5 seconds at 60fps
    # Stun timers
    player_stunned = False
    ai_stunned = False
    player_stun_timer = 0
    ai_stun_timer = 0
    stun_duration = 30  # frames (0.5 seconds at 60fps)

    # Countdown before starting
    countdown()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not player_stunned and player_missile_cooldown <= 0:
                    # Fire player missile
                    missile_rect = pygame.Rect(player_rect.right, player_rect.centery - 5, 10, 10)
                    missiles.append({'rect': missile_rect, 'type': 'player'})
                    player_missile_cooldown = missile_cooldown_frames

        # Update missile cooldowns
        if player_missile_cooldown > 0:
            player_missile_cooldown -= 1
        if ai_missile_cooldown > 0:
            ai_missile_cooldown -= 1

        # Update power-up timers
        if player_tall_paddle_timer > 0:
            player_tall_paddle_timer -= 1
        if player_fast_movement_timer > 0:
            player_fast_movement_timer -= 1
        if ai_tall_paddle_timer > 0:
            ai_tall_paddle_timer -= 1
        if ai_fast_movement_timer > 0:
            ai_fast_movement_timer -= 1

        # Star power-up spawning
        if star_rect is None:
            star_spawn_timer += 1
            if star_spawn_timer >= star_spawn_interval:
                star_rect = pygame.Rect(SCREEN_WIDTH // 2 - 10, random.randint(50, SCREEN_HEIGHT - 50), 20, 20)
                star_type = random.choice(['yellow', 'blue', 'green'])
                star_spawn_timer = 0

        # AI missile firing
        if ai_missile_cooldown <= 0 and not ai_stunned and random.random() < 0.01:  # 1% chance per frame
            missile_rect = pygame.Rect(ai_rect.left - 10, ai_rect.centery - 5, 10, 10)
            missiles.append({'rect': missile_rect, 'type': 'ai'})
            ai_missile_cooldown = missile_cooldown_frames

        # Player movement (only if not stunned)
        if not player_stunned:
            keys = pygame.key.get_pressed()
            movement_speed = PADDLE_SPEED * 1.25 if player_fast_movement_timer > 0 else PADDLE_SPEED
            if (keys[pygame.K_UP] or keys[pygame.K_w]) and player_rect.top > 0:
                player_rect.y -= int(movement_speed)
            if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and player_rect.bottom < SCREEN_HEIGHT:
                player_rect.y += int(movement_speed)

        # AI movement (only if not stunned)
        if not ai_stunned:
            ai_movement_speed = PADDLE_SPEED * 1.25 if ai_fast_movement_timer > 0 else PADDLE_SPEED
            if ball_speed_x > 0 and random.random() < ai_miss_chance and not ai_miss and abs(ball_rect.centery - ai_rect.centery) < 100:
                ai_miss = True
                ai_miss_timer = random.randint(20, 40)  # frames to miss
            if ai_miss:
                ai_miss_timer -= 1
                if ai_miss_timer <= 0:
                    ai_miss = False
            if not ai_miss:
                if ai_rect.centery < ball_rect.centery and ai_rect.bottom < SCREEN_HEIGHT:
                    ai_rect.y += int(ai_movement_speed)
                elif ai_rect.centery > ball_rect.centery and ai_rect.top > 0:
                    ai_rect.y -= int(ai_movement_speed)
        else:
            pass

        # Update stun timers
        if player_stunned:
            player_stun_timer -= 1
            if player_stun_timer <= 0:
                player_stunned = False
        if ai_stunned:
            ai_stun_timer -= 1
            if ai_stun_timer <= 0:
                ai_stunned = False

        # Update missiles
        for missile in missiles[:]:
            if missile['type'] == 'player':
                missile['rect'].x += missile_speed
                if missile['rect'].x > SCREEN_WIDTH:
                    missiles.remove(missile)
                elif missile['rect'].colliderect(ai_rect) and not ai_stunned:
                    missiles.remove(missile)
                    ai_stunned = True
                    ai_stun_timer = stun_duration
                    if MISSILE_SOUND:
                        MISSILE_SOUND.play()
                elif star_rect and missile['rect'].colliderect(star_rect):
                    missiles.remove(missile)
                    # Apply power-up effect
                    if star_type == 'yellow':
                        ai_stunned = True
                        ai_stun_timer = stun_duration
                    elif star_type == 'blue':
                        player_tall_paddle_timer = power_up_duration
                    elif star_type == 'green':
                        player_fast_movement_timer = power_up_duration
                    if MISSILE_SOUND:
                        MISSILE_SOUND.play()
                    star_rect = None
                    star_type = None
            else:  # AI missile
                missile['rect'].x -= missile_speed
                if missile['rect'].x < 0:
                    missiles.remove(missile)
                elif missile['rect'].colliderect(player_rect) and not player_stunned:
                    missiles.remove(missile)
                    player_stunned = True
                    player_stun_timer = stun_duration
                    if MISSILE_SOUND:
                        MISSILE_SOUND.play()
                elif star_rect and missile['rect'].colliderect(star_rect):
                    missiles.remove(missile)
                    # Apply power-up effect
                    if star_type == 'yellow':
                        player_stunned = True
                        player_stun_timer = stun_duration
                    elif star_type == 'blue':
                        ai_tall_paddle_timer = power_up_duration
                    elif star_type == 'green':
                        ai_fast_movement_timer = power_up_duration
                    if MISSILE_SOUND:
                        MISSILE_SOUND.play()
                    star_rect = None
                    star_type = None

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
            # Check for winner before countdown
            if ai_score >= settings['WINNING_SCORE']:
                if CELEBRATION_SOUND:
                    CELEBRATION_SOUND.play()
                return 'AI'
            ball_countdown()
            # Show playing field and wait 1 second
            screen.fill(BLACK)
            pygame.draw.rect(screen, WHITE, player_rect)
            pygame.draw.rect(screen, WHITE, ai_rect)
            pygame.draw.aaline(screen, WHITE, (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT))
            draw_text(str(player_score), font_medium, WHITE, screen, SCREEN_WIDTH // 4, 40)
            draw_text(str(ai_score), font_medium, WHITE, screen, SCREEN_WIDTH * 3 // 4, 40)
            pygame.display.flip()
            pygame.time.wait(1000)
        if ball_rect.right >= SCREEN_WIDTH:
            player_score += 1
            ball_speed_x, ball_speed_y = reset_ball(ball_rect, direction=-1)
            ai_miss = False
            speed_multiplier = 1.0
            for _ in range(3):
                if MISS_SOUND:
                    MISS_SOUND.play()
                pygame.time.wait(60)
            # Check for winner before countdown
            if player_score >= settings['WINNING_SCORE']:
                if CELEBRATION_SOUND:
                    CELEBRATION_SOUND.play()
                return 'Player'
            ball_countdown()
            # Show playing field and wait 1 second
            screen.fill(BLACK)
            pygame.draw.rect(screen, WHITE, player_rect)
            pygame.draw.aaline(screen, WHITE, (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT))
            draw_text(str(player_score), font_medium, WHITE, screen, SCREEN_WIDTH // 4, 40)
            draw_text(str(ai_score), font_medium, WHITE, screen, SCREEN_WIDTH * 3 // 4, 40)
            pygame.display.flip()
            pygame.time.wait(1000)

        # Draw everything
        screen.fill(BLACK)
        
        # Draw paddles with power-up effects
        player_paddle_height = PADDLE_HEIGHT * 1.5 if player_tall_paddle_timer > 0 else PADDLE_HEIGHT
        ai_paddle_height = PADDLE_HEIGHT * 1.5 if ai_tall_paddle_timer > 0 else PADDLE_HEIGHT
        
        player_paddle_rect = pygame.Rect(player_rect.x, player_rect.centery - player_paddle_height // 2, 
                                       PADDLE_WIDTH, player_paddle_height)
        ai_paddle_rect = pygame.Rect(ai_rect.x, ai_rect.centery - ai_paddle_height // 2, 
                                    PADDLE_WIDTH, ai_paddle_height)
        
        pygame.draw.rect(screen, WHITE, player_paddle_rect)
        pygame.draw.rect(screen, WHITE, ai_paddle_rect)
        pygame.draw.ellipse(screen, WHITE, ball_rect)
        pygame.draw.aaline(screen, WHITE, (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT))
        draw_text(str(player_score), font_medium, WHITE, screen, SCREEN_WIDTH // 4, 40)
        draw_text(str(ai_score), font_medium, WHITE, screen, SCREEN_WIDTH * 3 // 4, 40)
        
        # Draw missiles
        for missile in missiles:
            if missile['type'] == 'player':
                pygame.draw.rect(screen, (255, 0, 0), missile['rect'])  # Red for player
            else:
                pygame.draw.rect(screen, (0, 0, 255), missile['rect'])  # Blue for AI
        
        # Draw star power-up
        if star_rect:
            # Draw a proper star shape
            points = []
            center_x, center_y = star_rect.centerx, star_rect.centery
            radius_outer = 10
            radius_inner = 5
            for i in range(10):
                angle = i * 36 * numpy.pi / 180
                if i % 2 == 0:
                    x = center_x + radius_outer * numpy.cos(angle)
                    y = center_y + radius_outer * numpy.sin(angle)
                else:
                    x = center_x + radius_inner * numpy.cos(angle)
                    y = center_y + radius_inner * numpy.sin(angle)
                points.append((int(x), int(y)))
            
            if star_type == 'yellow':
                color = (255, 255, 0)  # Yellow
            elif star_type == 'blue':
                color = (0, 0, 255)    # Blue
            else:  # green
                color = (0, 255, 0)    # Green
            pygame.draw.polygon(screen, color, points)
        
        # Draw stun indicators
        if player_stunned:
            draw_text('STUNNED', font_small, (255, 0, 0), screen, SCREEN_WIDTH // 4, 80)
        if ai_stunned:
            draw_text('STUNNED', font_small, (255, 0, 0), screen, SCREEN_WIDTH * 3 // 4, 80)
        
        # Draw power-up indicators
        if player_tall_paddle_timer > 0:
            draw_text('TALL PADDLE', font_small, (0, 0, 255), screen, SCREEN_WIDTH // 4, 120)
        if player_fast_movement_timer > 0:
            draw_text('FAST MOVEMENT', font_small, (0, 255, 0), screen, SCREEN_WIDTH // 4, 160)
        if ai_tall_paddle_timer > 0:
            draw_text('TALL PADDLE', font_small, (0, 0, 255), screen, SCREEN_WIDTH * 3 // 4, 120)
        if ai_fast_movement_timer > 0:
            draw_text('FAST MOVEMENT', font_small, (0, 255, 0), screen, SCREEN_WIDTH * 3 // 4, 160)
        
        pygame.display.flip()
        clock.tick(60)

        # Check for winner (removed from here since it's now checked before countdown)


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
