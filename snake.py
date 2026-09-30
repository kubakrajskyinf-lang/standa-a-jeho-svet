import pygame
import random
import os

pygame.init()
pygame.mixer.init()

width, height = 600, 400
cell = 20

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Standa a jeho pivka")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 40)
small_font = pygame.font.SysFont(None, 28)

# 🔊 sounds
eat_sound = pygame.mixer.Sound("eat.wav")
beer_sound = pygame.mixer.Sound("beer.wav")
gameover_sound = pygame.mixer.Sound("game_over.wav")

yeah_sound = pygame.mixer.Sound("yeah.wav")
trava_sound = pygame.mixer.Sound("trava.wav")
trip_sound = pygame.mixer.Sound("trip.wav")

# 🎧 TRIP FIX (channel control)
trip_channel = pygame.mixer.Channel(5)
trip_active = False

# 🎵 music
pygame.mixer.music.load("hospoda.wav")
pygame.mixer.music.set_volume(0.4)
pygame.mixer.music.play(-1)

HIGH_FILE = "highscore.txt"

def load_highscore():
    if os.path.exists(HIGH_FILE):
        with open(HIGH_FILE, "r") as f:
            return int(f.read() or 0)
    return 0

def save_highscore(score):
    if score > load_highscore():
        with open(HIGH_FILE, "w") as f:
            f.write(str(score))

def rand_pos():
    return (random.randrange(0, width, cell),
            random.randrange(0, height, cell))

def spawn_food():
    r = random.random()

    if r < 0.1:
        return rand_pos(), "cocaine"
    elif r < 0.2:
        return rand_pos(), "weed"
    elif r < 0.25:
        return rand_pos(), "mushroom"
    elif r < 0.4:
        return rand_pos(), "beer"
    else:
        return rand_pos(), "normal"

def reset_game():
    return [(100, 100)], (cell, 0), *spawn_food(), 0, 6, False, None, 0


snake, direction, food, food_type, score, speed, game_over, powerup, powerup_end = reset_game()

state = "menu"
highscore = load_highscore()

weed_first_click = False
weed_last_time = 0
WEED_WINDOW = 250

running = True

# ================= LOOP =================
while running:
    now = pygame.time.get_ticks()

    trip_mode = (powerup == "mushroom")

    if trip_mode:
        screen.fill((random.randint(0,50), random.randint(0,50), random.randint(0,50)))
    else:
        screen.fill((0, 0, 0))

    # ================= EVENTS =================
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # MENU
        if state == "menu" and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                state = "game"
                pygame.mixer.music.stop()
                pygame.mixer.music.load("hudba.wav")
                pygame.mixer.music.set_volume(0.2)
                pygame.mixer.music.play(-1)

        # GAME INPUT
        if state == "game" and event.type == pygame.KEYDOWN:

            # RESTART
            if game_over and event.key == pygame.K_r:

                if trip_active:
                    trip_channel.stop()
                    trip_active = False

                snake, direction, food, food_type, score, speed, game_over, powerup, powerup_end = reset_game()
                pygame.mixer.music.load("hudba.wav")
                pygame.mixer.music.set_volume(0.2)
                pygame.mixer.music.play(-1)
                continue

            # WEED DOUBLE CLICK
            if powerup == "weed" and event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:

                if not weed_first_click:
                    weed_first_click = True
                    weed_last_time = now
                    continue
                else:
                    if now - weed_last_time <= WEED_WINDOW:
                        weed_first_click = False
                    else:
                        weed_first_click = True
                        weed_last_time = now
                        continue

            # MOVEMENT
            if event.key == pygame.K_UP and direction != (0, cell):
                direction = (0, -cell)
            elif event.key == pygame.K_DOWN and direction != (0, cell):
                direction = (0, cell)
            elif event.key == pygame.K_LEFT and direction != (cell, 0):
                direction = (-cell, 0)
            elif event.key == pygame.K_RIGHT and direction != (-cell, 0):
                direction = (cell, 0)

    # ================= MENU =================
    if state == "menu":
        screen.blit(font.render("Standa a jeho pivka", True, (255,255,255)), (120,120))
        screen.blit(small_font.render("ENTER", True, (180,180,180)), (200,180))
        screen.blit(small_font.render(f"Highscore: {highscore}", True, (255,215,0)), (200,240))
        pygame.display.flip()
        clock.tick(10)
        continue

    # ================= GRID =================
    offset = random.randint(-10, 10) if trip_mode else 0

    for x in range(0, width, cell):
        color = (random.randint(0,255), random.randint(0,255), random.randint(0,255)) if trip_mode else (30,30,30)
        pygame.draw.line(screen, color, (x+offset,0), (x+offset,height))

    for y in range(0, height, cell):
        color = (random.randint(0,255), random.randint(0,255), random.randint(0,255)) if trip_mode else (30,30,30)
        pygame.draw.line(screen, color, (0,y+offset), (width,y+offset))

    # ================= GAME =================
    if not game_over:
        head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

        if head[0] < 0 or head[0] >= width or head[1] < 0 or head[1] >= height or head in snake:
            game_over = True
            gameover_sound.play()
            pygame.mixer.music.stop()

            if trip_active:
                trip_channel.stop()
                trip_active = False

        snake.insert(0, head)

        if head == food:

            if food_type in ["cocaine", "weed", "mushroom"]:
                powerup = food_type

                # STOP TRIP IF RUNNING (important fix)
                if trip_active:
                    trip_channel.stop()
                    trip_active = False

                if powerup == "cocaine":
                    score += 5
                    powerup_end = now + 15000
                    yeah_sound.play()

                elif powerup == "weed":
                    score += 5
                    powerup_end = now + 15000
                    trava_sound.play()

                elif powerup == "mushroom":
                    score += 5
                    powerup_end = now + 20000
                    pygame.mixer.music.set_volume(0.05)

                    trip_channel.play(trip_sound, loops=-1)
                    trip_active = True

            elif food_type == "beer":
                score += 3
                beer_sound.play()

            else:
                score += 1
                eat_sound.play()

            food, food_type = spawn_food()

        else:
            snake.pop()

    # ================= POWERUP END =================
    if powerup and now >= powerup_end:

        if powerup == "mushroom" and trip_active:
            trip_channel.stop()
            trip_active = False

        powerup = None

    # ================= DRAW =================
    for i, seg in enumerate(snake):
        if trip_mode:
            color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
        else:
            color = (210,180,140) if i == 0 else ((0,120,255) if i%2==0 else (255,255,255))

        pygame.draw.rect(screen, color, (*seg, cell, cell))

    # ================= FOOD =================
    if food_type == "cocaine":
        pygame.draw.rect(screen, (255,255,255), (*food, cell, cell))
    elif food_type == "weed":
        pygame.draw.rect(screen, (0,255,0), (*food, cell, cell))
    elif food_type == "mushroom":
        pygame.draw.rect(screen, (255,0,0), (*food, cell, cell))
        pygame.draw.rect(screen, (255,255,255), (food[0], food[1], cell, 6))
    elif food_type == "beer":
        pygame.draw.rect(screen, (255,200,0), (*food, cell, cell))
        pygame.draw.rect(screen, (255,255,255), (food[0], food[1], cell, 6))
    else:
        pygame.draw.rect(screen, (255,0,0), (*food, cell, cell))

    # ================= UI =================
    screen.blit(small_font.render(f"Score: {score}", True, (255,255,255)), (10,10))

    if powerup:
        remaining = max(0, (powerup_end - now)//1000)
        screen.blit(small_font.render(f"{powerup}: {remaining}s", True, (255,255,255)), (10,40))

    # ================= GAME OVER =================
    if game_over:
        save_highscore(score)
        highscore = load_highscore()

        screen.blit(font.render("GAME OVER", True, (255,255,255)), (200,140))
        screen.blit(small_font.render("R restart", True, (180,180,180)), (220,190))
        screen.blit(small_font.render(f"Highscore: {highscore}", True, (255,215,0)), (200,230))

    pygame.display.flip()

    final_speed = speed
    if powerup == "cocaine":
        final_speed *= 1.25
    elif powerup == "weed":
        final_speed *= 0.5

    clock.tick(max(5, int(final_speed)))

pygame.quit()