# Wormy (a Nibbles clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

import math
import pygame
import random
import sys

from pygame.locals import *


class Worm:
    def __init__(self, color, outline_color, start_direction, start_coord, controls):
        self.color = color
        self.outline_color = outline_color
        self.direction = start_direction
        self.coords = [{'x': start_coord[0], 'y': start_coord[1]},
                       {'x': start_coord[0] - 1, 'y': start_coord[1]},
                       {'x': start_coord[0] - 2, 'y': start_coord[1]}]
        self.controls = controls
        self.alive = True
        self.time_alive = 0

    def control_worm(self, key_input):
        # checks key input against the controls and returns a direction
        if (key_input == self.controls['left']) and self.direction != RIGHT:
            self.direction = LEFT
        elif (key_input == self.controls['right']) and self.direction != LEFT:
            self.direction = RIGHT
        elif (key_input == self.controls['up']) and self.direction != DOWN:
            self.direction = UP
        elif (key_input == self.controls['down']) and self.direction != UP:
            self.direction = DOWN
        elif key_input == K_ESCAPE:
            terminate()

    def check_death(self):
        # check if the worm has hit itself or the edge
        if self.coords[HEAD]['x'] == -1 or self.coords[HEAD]['x'] == CELLWIDTH or self.coords[HEAD]['y'] == -1 or \
                self.coords[HEAD]['y'] == CELLHEIGHT:
            self.alive = False

        for wormBody in self.coords[1:]:
            if wormBody['x'] == self.coords[HEAD]['x'] and wormBody['y'] == self.coords[HEAD]['y']:
                self.alive = False

    def check_grow(self, apples):
        # check if worm has eaten an apple
        no_apples_eaten = True
        new_apples = apples

        for i in range(len(apples)):
            if self.coords[HEAD]['x'] == apples[i]['x'] and self.coords[HEAD]['y'] == apples[i]['y']:
                # don't remove worm's tail segment
                new_apples[i] = getRandomLocation()  # set a new apple somewhere
                no_apples_eaten = False

        if no_apples_eaten:
            del self.coords[-1]  # remove worm's tail segment

        return new_apples

    def change_worm_head(self):
        # move the worm by adding a segment in the direction it is moving
        if self.direction == UP:
            new_head = {'x': self.coords[HEAD]['x'], 'y': self.coords[HEAD]['y'] - 1}
        elif self.direction == DOWN:
            new_head = {'x': self.coords[HEAD]['x'], 'y': self.coords[HEAD]['y'] + 1}
        elif self.direction == LEFT:
            new_head = {'x': self.coords[HEAD]['x'] - 1, 'y': self.coords[HEAD]['y']}
        elif self.direction == RIGHT:
            new_head = {'x': self.coords[HEAD]['x'] + 1, 'y': self.coords[HEAD]['y']}

        self.coords.insert(0, new_head)

    def __del__(self):
        print('Deleting Worm')



NUM_APPLES = 3
FPS = 15
WINDOWWIDTH = 1280
WINDOWHEIGHT = 960
CELLSIZE = 20
RADIUS = math.floor(CELLSIZE/2.5)
assert WINDOWWIDTH % CELLSIZE == 0, "Window width must be a multiple of cell size."
assert WINDOWHEIGHT % CELLSIZE == 0, "Window height must be a multiple of cell size."
CELLWIDTH = int(WINDOWWIDTH / CELLSIZE)
CELLHEIGHT = int(WINDOWHEIGHT / CELLSIZE)

#             R    G    B
WHITE     = (255, 255, 255)
BLACK     = (  0,   0,   0)
RED       = (255,   0,   0)
BLUE      = (  0,   0, 255)
DARKBLUE  = (  0,   0, 155)
GREEN     = (  0, 255,   0)
DARKGREEN = (  0, 155,   0)
DARKGRAY  = ( 40,  40,  40)
YELLOW = (255,255,0)
BGCOLOR = BLACK

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

HEAD = 0 # syntactic sugar: index of the worm's head

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    pygame.display.set_caption('BattleWorms')

    showStartScreen()
    while True:
        # create worms before each game
        w1 = Worm(
            color=GREEN,
            outline_color=DARKGREEN,
            start_direction=UP,
            start_coord=(6, CELLHEIGHT - 7),
            controls={'left': K_a, 'right': K_d, 'up': K_w, 'down': K_s}
        )

        w2 = Worm(
            color=BLUE,
            outline_color=DARKBLUE,
            start_direction=DOWN,
            start_coord=(CELLWIDTH - 7, 6),
            controls={'left': K_LEFT, 'right': K_RIGHT, 'up': K_UP, 'down': K_DOWN}
        )

        worms = [w1, w2]
        runGame(worms)
        showGameOverScreen()


def runGame(worms):
    game_over = False
    time_ms = 0

    # Initialize list of random apples
    apples = []
    for i in range(NUM_APPLES):
        apples.append(getRandomLocation())

    while not game_over:  # main game loop
        for event in pygame.event.get():  # event handling loop
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                # if the worm is alive, get user input for controlling the worm
                for w in worms:
                    if w.alive:
                        w.control_worm(event.key)

        # if worms are alive, check if they hit a wall, themselves, or an apple,
        # then update death, growth and movement accordingly
        num_dead_worms = 0
        for w in worms:
            if w.alive:
                w.check_death()
                w.check_grow(apples)
                w.change_worm_head()
            else:
                num_dead_worms += 1

        if time_ms >= 1000:
            for w in worms:
                if w.alive:
                    w.time_alive += 1
            time_ms = 0

        # end game if all worms are dead
        if num_dead_worms == len(worms):
            game_over = True
            print('Game Over!')
            for w in worms:
                w.__del__()

        DISPLAYSURF.fill(BGCOLOR)
        drawGrid()
        for w in worms:
            drawWorm(w)
        for apple in apples:
            drawApple(apple)
        drawScore(worms)
        pygame.display.update()
        ms_per_frame = FPSCLOCK.tick(FPS)
        time_ms += ms_per_frame


def drawPressKeyMsg():
    pressKeySurf = BASICFONT.render('Press any key to play.', True, YELLOW)
    pressKeyRect = pressKeySurf.get_rect()
    pressKeyRect.topleft = (WINDOWWIDTH - 200, WINDOWHEIGHT - 30)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)


def checkForKeyPress():
    if len(pygame.event.get(QUIT)) > 0:
        terminate()

    keyUpEvents = pygame.event.get(KEYUP)
    if len(keyUpEvents) == 0:
        return None
    if keyUpEvents[0].key == K_ESCAPE:
        terminate()
    return keyUpEvents[0].key


def showStartScreen():
    titleFont = pygame.font.Font('freesansbold.ttf', 100)
    titleSurf1 = titleFont.render('Battle', True, WHITE, DARKGRAY)
    titleSurf2 = titleFont.render('Worms', True, RED)

    degrees1 = 0
    degrees2 = 0
    while True:
        DISPLAYSURF.fill(BGCOLOR)
        rotatedSurf1 = pygame.transform.rotate(titleSurf1, degrees1)
        rotatedRect1 = rotatedSurf1.get_rect()
        rotatedRect1.center = (math.floor(WINDOWWIDTH / 2), math.floor(WINDOWHEIGHT / 2))
        DISPLAYSURF.blit(rotatedSurf1, rotatedRect1)

        rotatedSurf2 = pygame.transform.rotate(titleSurf2, degrees2)
        rotatedRect2 = rotatedSurf2.get_rect()
        rotatedRect2.center = (math.floor(WINDOWWIDTH / 2), math.floor(WINDOWHEIGHT / 2))
        DISPLAYSURF.blit(rotatedSurf2, rotatedRect2)

        drawPressKeyMsg()

        if checkForKeyPress():
            pygame.event.get() # clear event queue
            return
        pygame.display.update()
        FPSCLOCK.tick(FPS)
        degrees1 += 3 # rotate by 3 degrees each frame
        degrees2 += 7 # rotate by 7 degrees each frame


def terminate():
    pygame.quit()
    sys.exit()


def getRandomLocation():
    return {'x': random.randint(0, CELLWIDTH - 1), 'y': random.randint(0, CELLHEIGHT - 1)}


def showGameOverScreen():
    gameOverFont = pygame.font.Font('freesansbold.ttf', 150)
    gameSurf = gameOverFont.render('Game', True, WHITE)
    overSurf = gameOverFont.render('Over', True, WHITE)
    gameRect = gameSurf.get_rect()
    overRect = overSurf.get_rect()
    gameRect.midtop = (math.floor(WINDOWWIDTH / 2), 10)
    overRect.midtop = (math.floor(WINDOWWIDTH / 2), gameRect.height + 10 + 25)

    DISPLAYSURF.blit(gameSurf, gameRect)
    DISPLAYSURF.blit(overSurf, overRect)
    drawPressKeyMsg()
    pygame.display.update()
    pygame.time.wait(500)
    checkForKeyPress()  # clear out any key presses in the event queue

    while True:
        if checkForKeyPress():
            pygame.event.get()  # clear event queue
            return

def drawScore(worms):
    prev_y_location = -10  # used for location of each score display
    for i in range(len(worms)):
        # Scoring: 100pts per apple eaten, 5pts per second alive
        score = ((len(worms[i].coords) - 3) * 100) + (worms[i].time_alive * 5)
        scoreSurf = BASICFONT.render(f'Worm {i+1} Score: {score}', True, WHITE)
        scoreRect = scoreSurf.get_rect()
        scoreRect.topleft = (WINDOWWIDTH - 180, prev_y_location + 25)
        prev_y_location += 25
        DISPLAYSURF.blit(scoreSurf, scoreRect)


def drawWorm(worm):
    for coord in worm.coords:
        x = coord['x'] * CELLSIZE
        y = coord['y'] * CELLSIZE
        wormSegmentRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, worm.outline_color, wormSegmentRect)
        wormInnerSegmentRect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
        pygame.draw.rect(DISPLAYSURF, worm.color, wormInnerSegmentRect)


def drawApple(coord):
    x = coord['x'] * CELLSIZE
    y = coord['y'] * CELLSIZE
    xcenter = coord['x'] * CELLSIZE + math.floor(CELLSIZE/2)
    ycenter = coord['y'] * CELLSIZE+ math.floor(CELLSIZE/2)
    #appleRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
    #pygame.draw.rect(DISPLAYSURF, RED, appleRect)
    pygame.draw.circle(DISPLAYSURF, RED,(xcenter,ycenter),RADIUS)


def drawGrid():
    for x in range(0, WINDOWWIDTH, CELLSIZE): # draw vertical lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE): # draw horizontal lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH, y))


if __name__ == '__main__':
    main()