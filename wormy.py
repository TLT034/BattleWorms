# Wormy (a Nibbles clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

import math
import pygame
import random
import sys

from pygame.locals import *

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
        runGame()
        showGameOverScreen()


def runGame():
    game_over1 = False
    game_over2 = False

    # Set a random start point.
    startx = 6
    starty = CELLHEIGHT - 7
    p1_wormCoords = [{'x': startx, 'y': starty}, {'x': startx - 1, 'y': starty}, {'x': startx - 2, 'y': starty}]
    p1_direction = UP

    startx2 = CELLWIDTH - 7
    starty2 = 6
    p2_wormCoords = [{'x': startx2, 'y': starty2}, {'x': startx2 - 1, 'y': starty2}, {'x': startx2 - 2, 'y': starty2}]
    p2_direction = DOWN

    # Initialize list of random apples
    apples = []
    for i in range(NUM_APPLES):
        apples.append(getRandomLocation())

    print("Apples:", apples)

    while not game_over1 and not game_over2:  # main game loop
        for event in pygame.event.get(): # event handling loop
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                p1_direction = controlWorm(p1_direction, event.key, player=1)
                p2_direction = controlWorm(p2_direction, event.key, player=2)


        game_over1 = checkGameOver(p1_wormCoords)
        game_over2 = checkGameOver(p2_wormCoords)
        p1_wormCoords, apples = checkAppleEat(p1_wormCoords, apples)
        p2_wormCoords, apples = checkAppleEat(p2_wormCoords, apples)


        p1_newHead = changeWormHead(p1_direction, p1_wormCoords)
        p2_newHead = changeWormHead(p2_direction, p2_wormCoords)

        p1_wormCoords.insert(0, p1_newHead)  # have already removed the last segment
        p2_wormCoords.insert(0, p2_newHead)  # have already removed the last segment

        DISPLAYSURF.fill(BGCOLOR)
        drawGrid()
        drawWorm(p1_wormCoords)
        drawWorm(p2_wormCoords)
        for apple in apples:
            drawApple(apple)
        drawScore(len(p1_wormCoords) - 3)
        pygame.display.update()
        FPSCLOCK.tick(FPS)



def controlWorm(direction, keyInput, player):
    if (keyInput == K_LEFT and player == 2 or keyInput == K_a and player == 1) and direction != RIGHT:
        direction = LEFT
    elif (keyInput == K_RIGHT and player == 2 or keyInput == K_d and player == 1) and direction != LEFT:
        direction = RIGHT
    elif (keyInput == K_UP and player == 2 or keyInput == K_w and player == 1) and direction != DOWN:
        direction = UP
    elif (keyInput == K_DOWN and player == 2 or keyInput == K_s and player == 1) and direction != UP:
        direction = DOWN
    elif keyInput == K_ESCAPE:
        terminate()

    return direction



def changeWormHead(direction, wormCoords):
    # move the worm by adding a segment in the direction it is moving
    if direction == UP:
        head = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] - 1}
    elif direction == DOWN:
        head = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] + 1}
    elif direction == LEFT:
        head = {'x': wormCoords[HEAD]['x'] - 1, 'y': wormCoords[HEAD]['y']}
    elif direction == RIGHT:
        head = {'x': wormCoords[HEAD]['x'] + 1, 'y': wormCoords[HEAD]['y']}

    return head



def checkGameOver(wormCoords):
    # check if the worm has hit itself or the edge
    if wormCoords[HEAD]['x'] == -1 or wormCoords[HEAD]['x'] == CELLWIDTH or wormCoords[HEAD]['y'] == -1 or \
            wormCoords[HEAD]['y'] == CELLHEIGHT:
        return True  # game over
    for wormBody in wormCoords[1:]:
        if wormBody['x'] == wormCoords[HEAD]['x'] and wormBody['y'] == wormCoords[HEAD]['y']:
            return True  # game over

    return False  # Not game over



def checkAppleEat(wormCoords, apples):
    # check if worm has eaten an apple
    no_apples_eaten = True

    for i in range(len(apples)):
        if wormCoords[HEAD]['x'] == apples[i]['x'] and wormCoords[HEAD]['y'] == apples[i]['y']:
            # don't remove worm's tail segment
            apples[i] = getRandomLocation()  # set a new apple somewhere
            no_apples_eaten = False

    if no_apples_eaten:
        del wormCoords[-1]  # remove worm's tail segment

    return wormCoords, apples



def drawPressKeyMsg():
    pressKeySurf = BASICFONT.render('Press a key to play.', True, YELLOW)
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
    checkForKeyPress() # clear out any key presses in the event queue

    while True:
        if checkForKeyPress():
            pygame.event.get() # clear event queue
            return

def drawScore(score):
    scoreSurf = BASICFONT.render('Score: %s' % (score), True, WHITE)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WINDOWWIDTH - 120, 10)
    DISPLAYSURF.blit(scoreSurf, scoreRect)


def drawWorm(wormCoords):
    for coord in wormCoords:
        x = coord['x'] * CELLSIZE
        y = coord['y'] * CELLSIZE
        wormSegmentRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, DARKGREEN, wormSegmentRect)
        wormInnerSegmentRect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
        pygame.draw.rect(DISPLAYSURF, GREEN, wormInnerSegmentRect)


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