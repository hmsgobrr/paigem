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

class BG:
    def __init__(self, img_path, speed):
        self.img = pygame.image.load(img_path)
        self.y1 = SHEIGHT/2.0 - self.img.get_height()/2.0
        self.y2 = self.y1 - SHEIGHT
        self.speed = speed

    def update(self, dt):
        self.y1 += self.speed*dt
        if self.y1 >= SHEIGHT/2.0 - self.img.get_height()/2.0 + SHEIGHT:
            self.y1 = SHEIGHT/2.0 - self.img.get_height()/2.0 - SHEIGHT
        self.y2 += self.speed*dt
        if self.y2 >= SHEIGHT/2.0 - self.img.get_height()/2.0 + SHEIGHT:
            self.y2 = SHEIGHT/2.0 - self.img.get_height()/2.0 - SHEIGHT

    def draw(self):
        scr.blit(self.img, (SWIDTH/2.0 - self.img.get_width()/2.0, self.y1))
        scr.blit(self.img, (SWIDTH/2.0 - self.img.get_width()/2.0, self.y2))

class Player:
    def __init__(self, img_path, speed):
        self.original_img = pygame.image.load(img_path)
        self.img = pygame.transform.scale(self.original_img, (216, 48))
        self.pos = [SWIDTH/2.0 - self.img.get_width(), SHEIGHT-90]
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

        if self.pos[0] < self.img.get_width()/-6.0:
            self.pos[0] = SWIDTH - self.img.get_width()/6.0
        elif self.pos[0] > SWIDTH - self.img.get_width()/6.0:
            self.pos[0] = self.img.get_width()/-6.0  

    def draw(self):
        if self.facingLeft:
            frameOffsetX = 0 if self.barkMeter > 0.0 else 108
            scr.blit(pygame.transform.flip(self.img, True, False), (self.pos[0], self.pos[1]), (54*self.frame + frameOffsetX, 0, 54, 48))
        else:
            frameOffsetX = 108 if self.barkMeter > 0.0 else 0
            scr.blit(self.img, (self.pos[0], self.pos[1]), (54*self.frame + frameOffsetX, 0, 54, 48))

    # def sizeUp(self):
        # self.img = pygame.transform.scale(self.original_img, (self.img.get_width()+1, self.img.get_height()+1))

class Obj:
    def __init__(self, img_path, index):
        self.img = pygame.image.load(img_path)
        self.img = pygame.transform.scale(self.img, (17, 32))
        # xPos = random.randint(0, SWIDTH - 17) if index == 0 else bepises[index-1].pos[0] + -200 if random.randint(0, 1) == 0 else 200
        # if xPos > SWIDTH-17:
            # xPos = SWIDTH-17
        # elif xPos < 0:
            # xPos = 0
        self.pos = [random.randint(0, SWIDTH - 17), -50 + index*-OBJDIST]

    def update(self, dt):
        self.pos[1] += OBJSPEED*dt

        objRect = Rect(self.pos[0], self.pos[1], self.img.get_width(), self.img.get_height())
        playerRect = Rect(player.pos[0], player.pos[1], player.img.get_width()/PLAYER_MAX_FRAME, player.img.get_height())

        if self.pos[1] > SHEIGHT or objRect.colliderect(playerRect):
            # newX = min(bepises, key=lambda b: b.pos[1]).pos[0] + -200 if random.randint(0, 1) == 0 else 200
            # if newX > SWIDTH-17:
                # newX = SWIDTH-17
            # elif newX < 0:
                # newX = 0
            newY = min(bepises, key=lambda b: b.pos[1]).pos[1] - OBJDIST
            if newY > -32:
                newY -= 100
            self.pos = [random.randint(0, SWIDTH - 17), newY]

            if objRect.colliderect(playerRect):
                player.barkMeter = 0.25
                pygame.mixer.Sound.play(barkSfx)

                global score
                score += 1

    def draw(self):
        scr.blit(self.img, (self.pos[0], self.pos[1]))

pygame.init()
clock = pygame.time.Clock()
scr = pygame.display.set_mode((600, 480))

bg = BG(os.path.join("./", "doge.png"), 30)
player = Player(os.path.join("./", "doge-sheet.png"), 300)
bepises = []
for i in range(10):
    bepises.append(Obj(os.path.join("./", "bepis.png"), i))

barkSfx = pygame.mixer.Sound(os.path.join("./", "bark.wav"))

score = 0

font = pygame.font.Font(os.path.join("./", "font.ttf"), 24)

while True:
    dt = clock.tick(30)/1000.0

    for event in pygame.event.get():
        if (event.type == pygame.QUIT) or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            sys.exit()

    scr.fill((0, 0, 0))

    bg.update(dt)    
    bg.draw()

    for bepis in bepises:
        bepis.update(dt)
        bepis.draw()

    player.update(dt)
    player.draw()

    scr.blit(font.render("SCORE: " + str(score), True, pygame.Color(255, 255, 255)), (10, 10))
    scr.blit(font.render("FPS: " + str(int(1/dt)), True, pygame.Color(255, 255, 255)), (520, 10))

    pygame.display.update()
