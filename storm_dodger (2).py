import pygame
import random
import os
import math

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 480, 750
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bhagam Bhag")
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

player_img = pygame.transform.scale(
    pygame.image.load("game/assets/images/player.png").convert_alpha(), (80, 100)
)

cyclone_base = pygame.transform.scale(
    pygame.image.load("game/assets/images/cyclone.png").convert_alpha(), (80, 90)
)
hail_img = pygame.transform.scale(
    pygame.image.load("game/assets/images/hailstorm.png").convert_alpha(), (80, 90)
)
lightning_img = pygame.transform.scale(
    pygame.image.load("game/assets/images/lightning.png").convert_alpha(), (80, 90)
)
tornado_img = pygame.transform.scale(
    pygame.image.load("game/assets/images/tornado.png").convert_alpha(), (80, 90)
)

mute_img = pygame.transform.scale(
    pygame.image.load("game/assets/ui/mute.png").convert_alpha(), (45, 45)
)
unmute_img = pygame.transform.scale(
    pygame.image.load("game/assets/ui/unmute.png").convert_alpha(), (45, 45)
)
play_img = pygame.transform.scale(
    pygame.image.load("game/assets/ui/play-button.png").convert_alpha(), (45, 45)
)
pause_img = pygame.transform.scale(
    pygame.image.load("game/assets/ui/pause-button.png").convert_alpha(), (45, 45)
)

font = pygame.font.SysFont("arial", 26)
bold_font = pygame.font.SysFont("arial", 40, bold=True)
small_bold = pygame.font.SysFont("arial", 28, bold=True)

RUNNING, PAUSED, GAME_OVER, LEVEL_UP = 1,2,3,4
state = RUNNING
pending_level = 1

pause_rect = pause_img.get_rect(topright=(WIDTH-10, 20))
mute_rect = mute_img.get_rect(topright=(WIDTH-10, 80))

def reset_game():
    global player, obstacles, score, level, spawn_timer, state
    player = pygame.Rect(WIDTH//2-40, HEIGHT-120, 80,100)
    obstacles=[]
    score=0
    level=1
    spawn_timer=0
    state=RUNNING

reset_game()
muted=False
base_speed=6
angle=0

dragging = False   # <--- NEW

while True:
    clock.tick(60)

    if level==1:
        speed=base_speed; bg=bg1
    elif level==2:
        speed=int(base_speed*1.15); bg=bg2
    else:
        speed=int(base_speed*1.20); bg=bg3

    win.blit(bg,(0,0))

    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            pygame.quit(); quit()

        if event.type in [pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN]:
            if event.type == pygame.FINGERDOWN:
                mx,my = event.x*WIDTH, event.y*HEIGHT
            else:
                mx,my = event.pos

            if pause_rect.collidepoint(mx,my):
                state = PAUSED if state==RUNNING else RUNNING

            if mute_rect.collidepoint(mx,my):
                muted = not muted
                pygame.mixer.music.set_volume(0 if muted else 0.5)

            if player.collidepoint(mx,my):
                dragging = True

            if state==GAME_OVER:
                reset_game()

            elif state==LEVEL_UP:
                level = pending_level
                obstacles.clear()
                spawn_timer = 0
                state = RUNNING

        if event.type in [pygame.MOUSEBUTTONUP, pygame.FINGERUP]:
            dragging = False

        if event.type in [pygame.MOUSEMOTION, pygame.FINGERMOTION] and dragging and state==RUNNING:
            if event.type == pygame.FINGERMOTION:
                mx = event.x * WIDTH
            else:
                mx = event.pos[0]
            player.centerx = mx

    if player.left < 0: player.left = 0
    if player.right > WIDTH: player.right = WIDTH

    if state==RUNNING:
        spawn_timer+=1
        if spawn_timer>40:
            spawn_timer=0
            kind=random.choice(["cyclone","hail","lightning","tornado"])
            obstacles.append([pygame.Rect(random.randint(40,WIDTH-40),-80,80,90),kind])

    angle+=2
    for obs in obstacles[:]:
        if state==RUNNING:
            obs[0].y+=speed

        if obs[0].top>HEIGHT:
            obstacles.remove(obs)
            score+=100
            if score>=1000 and level==1:
                pending_level=2; state=LEVEL_UP
            if score>=2000 and level==2:
                pending_level=3; state=LEVEL_UP

        if obs[0].colliderect(player):
            state=GAME_OVER
            if score>high_score:
                high_score=score
                high_level=max(high_level,level)
                with open(SAVE_FILE,"w") as f:
                    f.write(f"{high_score},{high_level}")

    win.blit(player_img,player)

    for rect,kind in obstacles:
        if kind=="cyclone":
            r=pygame.transform.rotate(cyclone_base,angle)
            win.blit(r,r.get_rect(center=rect.center))
        elif kind=="hail": win.blit(hail_img,rect)
        elif kind=="lightning": win.blit(lightning_img,rect)
        else: win.blit(tornado_img,rect)

    win.blit(font.render(f"Score: {score}",1,(255,255,255)),(10,10))
    win.blit(font.render(f"Best: {high_score}",1,(255,255,0)),(10,40))
    win.blit(font.render(f"Level: {level}",1,(106,50,159)),(10,70))
    win.blit(font.render(f"Max: {high_level}",1,(255,128,0)),(10,100))

    win.blit(pause_img if state==RUNNING else play_img, pause_rect)
    win.blit(unmute_img if muted else mute_img, mute_rect)

    if state == GAME_OVER:
        win.blit(bold_font.render("GAME OVER", True, (255,0,100)), (120,200))
        win.blit(small_bold.render("Tap to Restart", True, (102,101,45)), (120,250))

    if state==LEVEL_UP:
        win.blit(bold_font.render(f"Level {pending_level} Unlocked !",1,(80,0,120)),(90,300))
        win.blit(bold_font.render("Tap to Continue",1,(102,101,45)),(120,350))

    pygame.display.update()
