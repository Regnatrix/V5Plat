import pygame
from pygame import *


WIN_WIDTH = 800
WIN_HEIGHT = 600
HALF_WIDTH = int(WIN_WIDTH / 2)
HALF_HEIGHT = int(WIN_HEIGHT / 2)

DISPLAY = (WIN_WIDTH, WIN_HEIGHT)
DEPTH = 32
FLAGS = 0
CAMERA_SLACK = 30

def main():
    global cameraX, cameraY
    pygame.init()
    screen = pygame.display.set_mode(DISPLAY, FLAGS, DEPTH)
    pygame.display.set_caption("Use arrows to move!")
    timer =  pygame.time.Clock()

    bgfile = "Background.png"
    up = down = left = right = running = False
    bg = pygame.image.load(bgfile).convert()
    entities = pygame.sprite.Group()
    player = Player(32, 32)
    platforms = []

    x = y = 0
    level =  ["ppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppp",
              "p              p                                              p",
              "pppp           p              pppppppp                        E",
              "p              p                           p              ppppp",
              "p              p                           p      pp          p",
              "p    pppppppppppppp                        p                  p",
              "p                           pp             p                  p",
              "p                                      ppppppppppp            p",
              "p                                                             p",
              "p              ppppppppppp                                    p",
              "p         pppppp                                    pp        p",
              "p             p                                               p",
              "p             p     ppp                                       p",
              "p             p            pppppppp           ppp          pppp",
              "p             p                               p               p",
              "p             ppp                             p               p",
              "p             p      pp                       p     pp        p",
              "p             p       p     p     pppp        p               p",
              "p     pp  ppppppppppppp                       p               p",
              "p     pp                        pp            p         pp    p",
              "p     pp          pp                          p               p",
              "p     pp          p                           p               p",
              "ppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppp"]

    for row in level:
        for col in row:
            if col == "p":
                p = Platform(x, y)
                platforms.append(p)
                entities.add(p)
            if col == "E":
                e = ExitBlock(x, y)
                platforms.append(e)
                entities.add(e)
            x += 32
        y += 32
        x = 0

    total_level_width = len(level[0])*32
    total_level_height = len(level)*32
    camera = Camera(complex_camera, total_level_width, total_level_height)
    entities.add(player)

    while 1:
        timer.tick(60)

        for e in pygame.event.get():
            if e.type == QUIT:  raise SystemExit ( "QUIT" )
            if e.type == KEYDOWN and e.key == K_ESCAPE:
                raise SystemExit ( "ESCAPE" )
            if e.type == KEYDOWN and e.key == K_UP:
                up = True
            if e.type == KEYDOWN and e.key == K_DOWN:
                down = True
            if e.type == KEYDOWN and e.key == K_LEFT:
                left = True
            if e.type == KEYDOWN and e.key == K_RIGHT:
                right = True
            if e.type == KEYDOWN and e.key == K_SPACE:
                running = True

            if e.type == KEYUP and e.key == K_UP:
                up = False
            if e.type == KEYUP and e.key == K_DOWN:
                down = False
            if e.type == KEYUP and e.key == K_RIGHT:
                right = False
            if e.type == KEYUP and e.key == K_LEFT:
                left = False

        #for y in range(32):
        #    for x in range(32):
         #       screen.blit(bg, (x * 32, y * 32))
        screen.blit(bg, (0, 0))

        camera.update(player)

        player.update(up, down, left, right, running, platforms)
        for e in entities:
            screen.blit(e.image, camera.apply(e))

        pygame.display.update()

class Camera(object):
    def __init__(self, camera_func, width, height):
        self.camera_func = camera_func
        self.state = Rect(0, 0, width, height)

    def apply(self, target):
        return target.rect.move(self.state.topleft)

    def update(self, target):
        self.state = self.camera_func(self.state, target.rect)

def simple_camera(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    return Rect(-l+HALF_WIDTH, -t+HALF_HEIGHT, w, h)

def complex_camera(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    l, t, _, _ = -l+HALF_WIDTH, -t+HALF_HEIGHT, w, h

    l = min(0, l)
    l = max(-(camera.width-WIN_WIDTH), l)
    t = max(-(camera.height-WIN_HEIGHT), t)
    t = min(0, t)
    return Rect(l, t, w, h)

class Entity(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

class Player(Entity):
    def __init__(self, x, y):
        Entity.__init__(self)
        self.xvel = 0
        self.yvel = 0
        self.onGround = False
        self.image = pygame.image.load("stelpa.jpg")
        self.rect = Rect(x, y, 32, 32)

    def update(self, up, down, left, right, running, platforms):
        if up:
            if self.onGround: self.yvel -= 9
        if down:
            pass
        if running:
            self.xvel = 12
        if left:
            self.xvel = -8
        if right:
            self.xvel = 8
        if not self.onGround:
            self.yvel += 0.3
            if self.yvel > 100: self.yvel = 100
        if not(left or right):
            self.xvel = 0

        self.rect.left += self.xvel
        self.collide(self.xvel, 0, platforms)
        self.rect.top += self.yvel
        self.onGround = False
        self.collide(0, self.yvel, platforms)

    def collide(self, xvel, yvel, platforms):
        for p in platforms:
            if pygame.sprite.collide_rect(self, p):
                if isinstance(p, ExitBlock):
                    pygame.event.post(pygame.event.Event(QUIT))
                if xvel > 0:
                    self.rect.right = p.rect.left
                    print ("collide right")
                if xvel < 0:
                    self.rect.left = p.rect.right
                    print ("collide left")
                if yvel > 0:
                    self.rect.bottom = p.rect.top
                    self.onGround = True
                    self.yvel = 0
                if yvel < 0:
                    self.rect.top = p.rect.bottom

class Platform(Entity):
    def __init__(self, x, y):
        Entity.__init__(self)
       # self.image = Surface((32, 32))
       # self.image.convert()
       # self.image.fill(Color("#DDDDDD"))
        self.image = pygame.image.load("brick.png")
        self.rect = Rect(x, y, 32, 32)

    def update(self):
        pass

class ExitBlock(Platform):
    def __init__(self, x, y):
        Platform.__init__(self, x, y)
        self.image = Surface((32, 32))
        self.image.convert()
        self.image.fill(Color("#FFFFFF"))
        self.rect = Rect(x, y, 32, 32)

if __name__ == '__main__':
    main ()



