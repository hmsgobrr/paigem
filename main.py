import pygame
import sys
import os
import random
from pygame.locals import *

SWIDTH  = 600
SHEIGHT = 480

OBJSPEED = 200
OBJDIST = 70

PLAYER_MAX_FRAME = 5
EXPLOSION_MAX_FRAME = 6

BEPIS_BAR_DECREASE_SPEED = 15
BEPIS_BAR_INCREASE_SPEED = 15

PLAYER_MOUSECLICK_STOP_RANGE = 6

bepisImg = pygame.image.load(os.path.join("./", "bepis.png"))
bepisImg = pygame.transform.scale(bepisImg, (17, 32))
bombImg = pygame.image.load(os.path.join("./", "bomb.png"))

dogeImg = pygame.image.load(os.path.join("./", "doge-sheet.png"))
dogeImg = pygame.transform.scale(dogeImg, (54*PLAYER_MAX_FRAME, 48))

explosionImg = pygame.image.load(os.path.join("./", "explosion.png"))
explosionImg = pygame.transform.scale(explosionImg, (384, 64))

bepisBarImg = pygame.image.load(os.path.join("./", "bepisbar.png"))
bepisBarImg = pygame.transform.scale(bepisBarImg, (96*2, 30))

bg = pygame.image.load(os.path.join("./", "bg.png"))
bg = pygame.transform.scale(bg, (600, 480))

isOver = False
isGameStart = False
deathMessage = ""

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

class BepisBar:
    def __init__(self):
        self.bepisMeter = 100.0

    def update(self, dt):
        self.bepisMeter -= dt*BEPIS_BAR_DECREASE_SPEED
        if self.bepisMeter > 100:
            self.bepisMeter = 100
        if self.bepisMeter < 0:
            pygame.mixer.Sound.play(deathSfx)
            global isOver, deathMessage
            deathMessage = "Doge is out of bepis"
            isOver = True

    def draw(self):
        scr.blit(font.render("Bepis Bar", True, pygame.Color(0, 0, 0)), (200, 7))
        scr.blit(bepisBarImg, (100, 7), (0, 0, 96, 30))
        scr.blit(bepisBarImg, (100, 7), (96, 0, self.bepisMeter/100*96, 30))

class Player:
    def __init__(self, speed):
        self.pos = [SWIDTH/2.0 - dogeImg.get_width(), SHEIGHT-70]
        self.speed = speed
        self.barkMeter = 0.0
        self.facingLeft = False
        self.frame = 0
        self.frameAcc = 0.0

        self.isChasingMouseClick = False
        self.lastMouseClick = [0, 0]

    def update(self, dt):
        k = pygame.key.get_pressed()
        if k[K_d] or k[K_RIGHT]:
            self.isChasingMouseClick = False

            move =  1
        elif k[K_a] or k[K_LEFT]:
            self.isChasingMouseClick = False
            
            move = -1
        else:
            move =  0

        if pygame.mouse.get_pressed()[0]:
            self.isChasingMouseClick = True
            self.lastMouseClick[0] = pygame.mouse.get_pos()[0]

        mousePosCurrentPosDifference = self.lastMouseClick[0] - self.pos[0]
        if self.isChasingMouseClick and abs(mousePosCurrentPosDifference) > PLAYER_MOUSECLICK_STOP_RANGE:
            move = 1 if mousePosCurrentPosDifference > 0 else -1

        self.facingLeft = move < 0

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
            flippedImg = pygame.transform.flip(dogeImg, True, False)
            if isOver:
                scr.blit(flippedImg, (self.pos[0], self.pos[1]), (0, 0, 54, 48))
                return
            frameOffsetX = 54 if self.barkMeter > 0.0 else 162
            scr.blit(flippedImg, (self.pos[0], self.pos[1]), (54*self.frame + frameOffsetX, 0, 54, 48))
        else:
            if isOver:
                scr.blit(dogeImg, (self.pos[0], self.pos[1]), (54*4, 0, 54, 48))
                return
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
                    pygame.mixer.Sound.play(explosionSfx)
                    global isOver, deathMessage
                    deathMessage = "Doge is ded"
                    isOver = True
                else:
                    player.barkMeter = 0.25
                    pygame.mixer.Sound.play(barkSfx)
                    bepisBar.bepisMeter += BEPIS_BAR_INCREASE_SPEED
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
pygame.display.toggle_fullscreen()

player = Player(300)
bepises = []
for i in range(5):
    bepises.append(Obj(i))
score = 0
explosion = Explosion()
bepisBar = BepisBar()

barkSfx = pygame.mixer.Sound(os.path.join("./", "bark.wav"))
explosionSfx = pygame.mixer.Sound(os.path.join("./", "explosion.wav"))
deathSfx = pygame.mixer.Sound(os.path.join("./", "death.wav"))
font = pygame.font.Font(os.path.join("./", "font.ttf"), 24)

def initGame():
    global isOver, player, bepises, score, explosion, bepisBar
    isOver = False
    player.__init__(300)
    bepises = []
    for i in range(5):
        bepises.append(Obj(i))
    score = 0
    explosion.__init__()
    bepisBar.__init__()

def updateGame(dt):
    if isOver or not isGameStart:
        return

    for bepis in bepises:
        bepis.update(dt)

    player.update(dt)

    bepisBar.update(dt)

def drawGame():
    for bepis in bepises:
        bepis.draw()

    player.draw()
    explosion.draw()

    bepisBar.draw()

    scr.blit(font.render("SCORE: " + str(score), True, pygame.Color(0, 0, 0)), (10, 10))
    scr.blit(font.render("FPS: " + str(int(1/dt)), True, pygame.Color(0, 0, 0)), (520, 10))

def gameOverScreen():
    textW, _ = font.size(deathMessage+". [SPACE] to retry")
    scr.blit(font.render(deathMessage+". [SPACE] to retry", True, pygame.Color(0, 0, 0)), (SWIDTH/2 - textW/2, SHEIGHT/2 - 40))

    k = pygame.key.get_pressed()
    if k[K_SPACE]:
        initGame()

def mainMenuScreen():
    textW, _ = font.size("Welcome to Bepis Adventures.")
    scr.blit(font.render("Welcome to Bepis Adventures.", True, pygame.Color(0, 0, 0)), (SWIDTH/2 - textW/2, SHEIGHT/2 - 60))
    textW, _ = font.size("[SPACE] to play")
    scr.blit(font.render("[SPACE] to play", True, pygame.Color(0, 0, 0)), (SWIDTH/2 - textW/2, SHEIGHT/2 - 20))

    k = pygame.key.get_pressed()
    if k[K_SPACE]:
        global isGameStart
        isGameStart = True

while True:
    dt = clock.tick(30)/1000.0

    for event in pygame.event.get():
        if (event.type == pygame.QUIT) or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            sys.exit()

    updateGame(dt)

    explosion.update(dt)

    scr.fill((0, 0, 0))
    scr.blit(bg, (0, 0))

    if isGameStart:
        drawGame()
    else:
        mainMenuScreen()

    if isOver:
        gameOverScreen()

    pygame.display.update()
