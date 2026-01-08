import pygame, random, os, time

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 480, 750
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("STORM DOGDER")
clock = pygame.time.Clock()

# ---------------- SAVE ----------------
SAVE_FILE = "progress.txt"
if os.path.exists(SAVE_FILE):
    with open(SAVE_FILE, "r") as f:
        high_score, high_level = map(int, f.read().split(","))
else:
    high_score, high_level = 0, 1

# ---------------- MUSIC ----------------
pygame.mixer.music.load("game/assets/music/music.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

# ---------------- IMAGES ----------------
bg1 = pygame.image.load("game/assets/images/background.png").convert()
bg2 = pygame.image.load("game/assets/images/background_image_2.png").convert()
bg3 = pygame.image.load("game/assets/images/background_image_3.png").convert()

player_img = pygame.transform.scale(pygame.image.load("game/assets/images/player.png").convert_alpha(), (80,100))
cyclone_base = pygame.transform.scale(pygame.image.load("game/assets/images/cyclone.png").convert_alpha(), (80,90))
hail_img = pygame.transform.scale(pygame.image.load("game/assets/images/hailstorm.png").convert_alpha(), (80,90))
lightning_img = pygame.transform.scale(pygame.image.load("game/assets/images/lightning.png").convert_alpha(), (80,90))
tornado_img = pygame.transform.scale(pygame.image.load("game/assets/images/tornado.png").convert_alpha(), (80,90))

star_img = pygame.transform.scale(pygame.image.load("game/assets/images/star.png").convert_alpha(), (40,40))
heart2_img = pygame.transform.scale(pygame.image.load("game/assets/images/heart.png").convert_alpha(), (35,35))
heart_ui = pygame.transform.scale(pygame.image.load("game/assets/images/heart.png").convert_alpha(), (30,30))

mute_img = pygame.transform.scale(pygame.image.load("game/assets/ui/mute.png").convert_alpha(), (45,45))
unmute_img = pygame.transform.scale(pygame.image.load("game/assets/ui/unmute.png").convert_alpha(), (45,45))
play_img = pygame.transform.scale(pygame.image.load("game/assets/ui/play-button.png").convert_alpha(), (45,45))
pause_img = pygame.transform.scale(pygame.image.load("game/assets/ui/pause-button.png").convert_alpha(), (45,45))

# ---------------- FONTS ----------------
font = pygame.font.SysFont("arial", 26)
bold_font = pygame.font.SysFont("arial", 40, bold=True)
small_bold = pygame.font.SysFont("arial", 28, bold=True)
bubble_font = pygame.font.SysFont("arial", 22, bold=True)

# ---------------- STATES ----------------
RUNNING, PAUSED, GAME_OVER, LEVEL_UP = 1,2,3,4
state = RUNNING
pending_level = 1

pause_rect = pause_img.get_rect(topright=(WIDTH-10,20))
mute_rect = mute_img.get_rect(topright=(WIDTH-10,80))

# ---------------- RESET ----------------
def reset_game():
    global player, obstacles, stars, hearts, floating_scores
    global score, level, spawn_timer, lives, invincible, inv_time, state
    player = pygame.Rect(WIDTH//2-40, HEIGHT-120, 80,100)
    obstacles = []
    stars = []
    hearts = []
    floating_scores = []
    score = 0
    level = 1
    spawn_timer = 0
    lives = 3
    invincible = False
    inv_time = 0
    state = RUNNING

reset_game()

base_speed = 6
angle = 0
dragging = False
muted = False

# ---------------- LOOP ----------------
while True:
    clock.tick(60)

    # Background + speed
    if level == 1:
        speed = base_speed; bg = bg1
    elif level == 2:                                    # increasing speed with change in level 
        speed = int(base_speed*1.15); bg = bg2
    else:
        speed = int(base_speed*1.2); bg = bg3

    win.blit(bg, (0,0))

    # ---------------- INPUT ----------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:                                            # user input response 
            pygame.quit(); quit()

        if event.type in [pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN]:
            if event.type == pygame.FINGERDOWN:
                mx,my = event.x*WIDTH, event.y*HEIGHT
            else:
                mx,my = event.pos

            if pause_rect.collidepoint(mx,my):
                state = PAUSED if state == RUNNING else RUNNING

            if mute_rect.collidepoint(mx,my):
                muted = not muted
                pygame.mixer.music.set_volume(0 if muted else 0.5)

            if player.collidepoint(mx,my) and state == RUNNING:
                dragging = True

            if state == GAME_OVER:
                reset_game()
            elif state == LEVEL_UP:
                level = pending_level
                obstacles.clear()
                spawn_timer = 0
                state = RUNNING

        if event.type in [pygame.MOUSEBUTTONUP, pygame.FINGERUP]:
            dragging = False

        if event.type in [pygame.MOUSEMOTION, pygame.FINGERMOTION] and dragging and state == RUNNING:
            if event.type == pygame.FINGERMOTION:
                player.centerx = event.x*WIDTH
            else:
                player.centerx = event.pos[0]

    # player position
    if player.left < 0: player.left = 0
    if player.right > WIDTH: player.right = WIDTH

    # ---------------- SPAWN ----------------
    if state == RUNNING:
        spawn_timer += 1
        if spawn_timer > 40:
            spawn_timer = 0
            obstacles.append([pygame.Rect(random.randint(40,WIDTH-40), -80, 80, 90),
                              random.choice(["cyclone","hail","lightning","tornado"])])

        if random.randint(1,300) == 1:
            stars.append(pygame.Rect(random.randint(40,WIDTH-40), -40, 40, 40))

        if random.randint(1,400) == 1:
            hearts.append(pygame.Rect(random.randint(40,WIDTH-40), -40, 35, 35))

    # ---------------- INVINCIBLE ----------------
    if invincible and time.time() > inv_time:
        invincible = False

    # ---------------- OBSTACLES ----------------
    for obs in obstacles[:]:
        if state == RUNNING:
            obs[0].y += speed

        if obs[0].top > HEIGHT:
            obstacles.remove(obs)
            score += 100                                                     # score setup
            floating_scores.append([obs[0].centerx, obs[0].y, 255])

            if score >= 2000 and level == 1:                                     # score setup levle wise 
                pending_level = 2; state = LEVEL_UP
            if score >= 3000 and level == 2:
                pending_level = 3; state = LEVEL_UP

        if obs[0].colliderect(player) and not invincible:
            obstacles.remove(obs)
            lives -= 1
            if lives <= 0:
                state = GAME_OVER                                        # saving and updating high score 
                if score > high_score:
                    high_score = score
                    high_level = max(high_level, level)
                    with open(SAVE_FILE,"w") as f:
                        f.write(f"{high_score},{high_level}")

    # ---------------- POWERUPS ----------------
    for s in stars[:]:
        if state == RUNNING: s.y += speed
        if s.colliderect(player):
            invincible = True
            inv_time = time.time() + 5                                    # invincibility for aur player for 5 seconds
            stars.remove(s)
        elif s.top > HEIGHT:
            stars.remove(s)

    for h in hearts[:]:
        if state == RUNNING: h.y += speed
        if h.colliderect(player):
            lives = min(4, lives+1)
            hearts.remove(h)                                   # life line after catching heart upto 
        elif h.top > HEIGHT:
            hearts.remove(h)

    # ---------------- DRAW ----------------
    win.blit(player_img, player)

    for r,k in obstacles:
        if k == "cyclone":
            img = pygame.transform.rotate(cyclone_base, angle)
            win.blit(img, img.get_rect(center=r.center))
        elif k == "hail": win.blit(hail_img, r)
        elif k == "lightning": win.blit(lightning_img, r)
        else: win.blit(tornado_img, r)

    for s in stars: win.blit(star_img, s)
    for h in hearts: win.blit(heart2_img, h)

    # Floating score
    for b in floating_scores[:]:
        b[1] -= 1
        b[2] -= 4
        surf = bubble_font.render("+100", True, (25,50,159))                 # floating bubble score 
        surf.set_alpha(b[2])
        win.blit(surf, (b[0], b[1]))
        if b[2] <= 0:
            floating_scores.remove(b)

    # UI
    win.blit(font.render(f"Score: {score}",1,(25,50,159)),(10,40))
    win.blit(font.render(f"Best: {high_score}",1,(106,50,159)),(10,70))
    win.blit(font.render(f"Level: {level}",1,(106,50,159)),(10,100))

    for i in range(lives):
        win.blit(heart_ui, (10 + i*35, 10))

    win.blit(pause_img if state==RUNNING else play_img, pause_rect)
    win.blit(unmute_img if muted else mute_img, mute_rect)

    if state == GAME_OVER:
        win.blit(bold_font.render("GAME OVER",1,(255,0,100)),(130,250))
        win.blit(small_bold.render("Tap to Restart",1,(158, 76, 103)),(130,300))

    if state == LEVEL_UP:
        win.blit(bold_font.render(f"Level {pending_level} Unlocked!",1,(80,0,120)),(80,300))
        win.blit(small_bold.render("Tap to Continue",1,(255,140,254)),(120,350))

    pygame.display.update()



