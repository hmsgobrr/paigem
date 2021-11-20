import pygame
import sys
import os
import random
from pygame.locals import *

SWIDTH  = 600
SHEIGHT = 480

OBJSPEED = 200
OBJDIST = 70

PLAYER_MAX_FRAME = 4
EXPLOSION_MAX_FRAME = 6

bepisImg = pygame.image.load(os.path.join("./", "bepis.png"))
bepisImg = pygame.transform.scale(bepisImg, (17, 32))
bombImg = pygame.image.load(os.path.join("./", "bomb.png"))

dogeImg = pygame.image.load(os.path.join("./", "doge-sheet.png"))
dogeImg = pygame.transform.scale(dogeImg, (216, 48))

explosionImg = pygame.image.load(os.path.join("./", "explosion.png"))
explosionImg = pygame.transform.scale(explosionImg, (384, 64))

isOver = False

class Explosion:
    def __init__(self):
        self.active = False
        self.frame = 0
        self.frameAcc = 0.0

    def explode(self):
        self.frame = 0
        self.frameAcc = 0.0
        self.active = True

    def update(self, dt):
        if not self.active:
            return

        self.frameAcc += dt
        if self.frameAcc >= 0.075:
            self.frame += 1
            self.frameAcc = 0.0

    def draw(self):
        if not self.active:
            return

        playerPos = (player.pos[0] + dogeImg.get_width()/PLAYER_MAX_FRAME/2, player.pos[1] + dogeImg.get_height()/2)
        explosionPos = (playerPos[0] - explosionImg.get_width()/EXPLOSION_MAX_FRAME/2, playerPos[1] - explosionImg.get_height()/2)
        scr.blit(explosionImg, explosionPos, (64*self.frame, 0, 64, 64))

class Player:
    def __init__(self, speed):
        self.pos = [SWIDTH/2.0 - dogeImg.get_width(), SHEIGHT-70]
        self.speed = speed
        self.barkMeter = 0.0
        self.facingLeft = False
        self.frame = 0
        self.frameAcc = 0.0

    def update(self, dt):
        k = pygame.key.get_pressed()
        if k[K_d] or k[K_RIGHT]:
            self.facingLeft = False
            move =  1
        elif k[K_a] or k[K_LEFT]:
            self.facingLeft = True
            move = -1
        else:
            move =  0
        self.pos[0] += move*self.speed*dt

        if self.barkMeter > 0.0:
            self.barkMeter -= dt

        self.frameAcc += dt
        if self.frameAcc >= 0.15 and move != 0:
            self.frame += 1
            self.frame %= 2
            self.frameAcc = 0.0

        if self.pos[0] < dogeImg.get_width()/-6.0:
            self.pos[0] = SWIDTH - dogeImg.get_width()/6.0
        elif self.pos[0] > SWIDTH - dogeImg.get_width()/6.0:
            self.pos[0] = dogeImg.get_width()/-6.0  

    def draw(self):
        if self.facingLeft:
            frameOffsetX = 0 if self.barkMeter > 0.0 else 108
            scr.blit(pygame.transform.flip(dogeImg, True, False), (self.pos[0], self.pos[1]), (54*self.frame + frameOffsetX, 0, 54, 48))
        else:
            frameOffsetX = 108 if self.barkMeter > 0.0 else 0
            scr.blit(dogeImg, (self.pos[0], self.pos[1]), (54*self.frame + frameOffsetX, 0, 54, 48))

class Obj:
    def __init__(self, index):
        self.pos = [random.randint(0, SWIDTH - 17), -50 + index*-OBJDIST]
        self.isBomb = True if random.randint(0, 5) == 0 else False

    def update(self, dt):
        self.pos[1] += OBJSPEED*dt

        objRect = Rect(self.pos[0], self.pos[1], bepisImg.get_width(), bepisImg.get_height())
        playerRect = Rect(player.pos[0], player.pos[1], dogeImg.get_width()/PLAYER_MAX_FRAME, dogeImg.get_height())

        if self.pos[1] > SHEIGHT or objRect.colliderect(playerRect):
            newY = min(bepises, key=lambda b: b.pos[1]).pos[1] - OBJDIST
            if newY > -32:
                newY -= 100
            self.pos = [random.randint(0, SWIDTH - 17), newY]

            if objRect.colliderect(playerRect):
                if self.isBomb:
                    explosion.explode()
                    global isOver
                    isOver = True
                else:
                    player.barkMeter = 0.25
                    pygame.mixer.Sound.play(barkSfx)
                    global score
                    score += 1

            self.isBomb = True if random.randint(0, 5) == 0 else False

    def draw(self):
        if self.isBomb:
            scr.blit(bombImg, (self.pos[0], self.pos[1]), (30*random.randint(0, 1), 0, 30, 30))
        else:
            scr.blit(bepisImg, (self.pos[0], self.pos[1]))

pygame.init()
clock = pygame.time.Clock()
scr = pygame.display.set_mode((600, 480))

bg = pygame.image.load(os.path.join("./", "bg.png"))
bg = pygame.transform.scale(bg, (600, 480))

player = Player(300)

bepises = []
for i in range(10):
    bepises.append(Obj(i))

barkSfx = pygame.mixer.Sound(os.path.join("./", "bark.wav"))

score = 0

font = pygame.font.Font(os.path.join("./", "font.ttf"), 24)

explosion = Explosion()

def updateGame(dt):
    if isOver:
        return

    for bepis in bepises:
        bepis.update(dt)

    player.update(dt)

def gameOverScreen():
    textW, textH = font.size("Doge is ded. [SPACE] to retry")
    scr.blit(font.render("Doge is ded. [SPACE] to retry", True, pygame.Color(0, 0, 0)), (SWIDTH/2 - textW/2, SHEIGHT/2 - 40))

    k = pygame.key.get_pressed()
    if k[K_SPACE]:
        global isOver
        isOver = False

while True:
    dt = clock.tick(30)/1000.0

    for event in pygame.event.get():
        if (event.type == pygame.QUIT) or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            sys.exit()

    updateGame(dt)

    explosion.update(dt)

    scr.fill((0, 0, 0))
    scr.blit(bg, (0, 0))

    for bepis in bepises:
        bepis.draw()

    player.draw()
    explosion.draw()

    scr.blit(font.render("SCORE: " + str(score), True, pygame.Color(0, 0, 0)), (10, 10))
    scr.blit(font.render("FPS: " + str(int(1/dt)), True, pygame.Color(0, 0, 0)), (520, 10))

    if isOver:
        gameOverScreen()

    pygame.display.update()
