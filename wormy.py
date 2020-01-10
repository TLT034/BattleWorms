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
    def __init__(self, name, inner_color, outline_color, start_direction, start_coord, controls):
        self.name = name
        self.inner_color = inner_color
        self.outline_color = outline_color
        self.direction = start_direction
        if start_direction == UP:
            self.coords = [
                {'x': start_coord[0], 'y': start_coord[1]},
                {'x': start_coord[0], 'y': start_coord[1] + 1},
                {'x': start_coord[0], 'y': start_coord[1] + 2}
            ]
            self.tongue_coords = [
                {'x': start_coord[0], 'y': start_coord[1] - 1},
                {'x': start_coord[0], 'y': start_coord[1] - 2},
            ]
        elif start_direction == DOWN:
            self.coords = [
                {'x': start_coord[0], 'y': start_coord[1]},
                {'x': start_coord[0], 'y': start_coord[1] - 1},
                {'x': start_coord[0], 'y': start_coord[1] - 2}
            ]
            self.tongue_coords = [
                {'x': start_coord[0], 'y': start_coord[1] + 1},
                {'x': start_coord[0], 'y': start_coord[1] + 2},
            ]
        elif start_direction == RIGHT:
            self.coords = [
                {'x': start_coord[0], 'y': start_coord[1]},
                {'x': start_coord[0] - 1, 'y': start_coord[1]},
                {'x': start_coord[0] - 2, 'y': start_coord[1]}
            ]
            self.tongue_coords = [
                {'x': start_coord[0] + 1, 'y': start_coord[1]},
                {'x': start_coord[0] + 2, 'y': start_coord[1]},
            ]
        elif start_direction == LEFT:
            self.coords = [
                {'x': start_coord[0], 'y': start_coord[1]},
                {'x': start_coord[0] + 1, 'y': start_coord[1]},
                {'x': start_coord[0] + 2, 'y': start_coord[1]}
            ]
            self.tongue_coords = [
                {'x': start_coord[0] - 1, 'y': start_coord[1]},
                {'x': start_coord[0] - 2, 'y': start_coord[1]},
            ]
        self.controls = controls
        self.alive = True
        self.life_duration = 0
        self.zombie = False
        self.zombie_time = 0
        self.biting = False
        self.biting_time = 0
        self.size_at_death = 0


    def __str__(self):
        return self.name


    def control_worm(self, key_input):
        # checks key input against the controls and returns a direction
        if (key_input == self.controls['left'] or key_input == K_KP4) and self.direction != RIGHT:
            self.direction = LEFT
        elif (key_input == self.controls['right'] or key_input == K_KP6) and self.direction != LEFT:
            self.direction = RIGHT
        elif (key_input == self.controls['up'] or key_input == K_KP8) and self.direction != DOWN:
            self.direction = UP
        elif (key_input == self.controls['down'] or key_input == K_KP2) and self.direction != UP:
            self.direction = DOWN
        elif key_input == self.controls['bite']:
            self.zombie = True
            self.biting = True
        elif key_input == K_ESCAPE:
            terminate()


    def check_death(self, other_worms, stones):
        # check if the worm has hit an edge
        if self.coords[HEAD]['x'] == -1 or self.coords[HEAD]['x'] == CELLWIDTH or self.coords[HEAD]['y'] == -1 or \
                self.coords[HEAD]['y'] == CELLHEIGHT:
            self.alive = False
            stone_coords = self.coords
            self.coords = []
            self.size_at_death = len(stone_coords)
            return stone_coords

        # check if the worm has hit itself
        for wormBody in self.coords[1:]:
            if wormBody['x'] == self.coords[HEAD]['x'] and wormBody['y'] == self.coords[HEAD]['y']:
                self.alive = False
                stone_coords = self.coords
                self.coords = []
                self.size_at_death = len(stone_coords)
                return stone_coords

        # check if the worm has hit another worm
        for other_w in other_worms:
            if not other_w == self:
                for other_body in other_w.coords:
                    if other_body['x'] == self.coords[HEAD]['x'] and other_body['y'] == self.coords[HEAD]['y']:
                        self.alive = False
                        stone_coords = self.coords
                        self.coords = []
                        self.size_at_death = len(stone_coords)
                        return stone_coords

        # check if the worm has hit a stone wall
        for stone in stones:
            if self.coords[HEAD]['x'] == stone['x'] and self.coords[HEAD]['y'] == stone['y']:
                self.alive = False
                stone_coords = self.coords
                self.coords = []
                self.size_at_death = len(stone_coords)
                return stone_coords


    def check_bitten(self, other_worms):
        for other_w in other_worms:
            if not other_w == self:
                # if another worm bites my body, all coords from where I was bit to my tail become a stone wall
                # if another worm bites my head, I die and turn to a stone wall
                for i in range(len(self.coords)):
                    for tongue_coord in other_w.tongue_coords:
                        if tongue_coord['x'] == self.coords[i]['x'] and tongue_coord['y'] == self.coords[i]['y'] and other_w.biting:
                            stone_coords = self.coords[i+1:]
                            for coord in self.coords[i:]:
                                self.coords.remove(coord)
                            if i == HEAD:
                                self.alive = False
                                self.size_at_death = len(stone_coords)
                            return stone_coords


    def check_grow(self, apples):
        # check if worm has eaten an apple
        no_apples_eaten = True
        new_apples = apples

        for i in range(len(apples)):
            if self.coords[HEAD]['x'] == apples[i]['x'] and self.coords[HEAD]['y'] == apples[i]['y']:
                # don't remove worm's tail segment
                new_apples[i] = getRandomLocation()  # set a new apple somewhere
                no_apples_eaten = False

        if no_apples_eaten or self.zombie:  # no points for apples if using zombie ability - ZOMBIES DON'T EAT APPLES!
            del self.coords[-1]  # remove worm's tail segment

        return new_apples


    def change_worm_head(self):
        # move the worm by adding a segment in the direction it is moving
        if self.direction == UP:
            new_head = {'x': self.coords[HEAD]['x'], 'y': self.coords[HEAD]['y'] - 1}
            self.tongue_coords = [
                {'x': self.coords[HEAD]['x'], 'y': self.coords[HEAD]['y'] - 2},
                {'x': self.coords[HEAD]['x'], 'y': self.coords[HEAD]['y'] - 3}
            ]
        elif self.direction == DOWN:
            new_head = {'x': self.coords[HEAD]['x'], 'y': self.coords[HEAD]['y'] + 1}
            self.tongue_coords = [
                {'x': self.coords[HEAD]['x'], 'y': self.coords[HEAD]['y'] + 2},
                {'x': self.coords[HEAD]['x'], 'y': self.coords[HEAD]['y'] + 3}
            ]
        elif self.direction == LEFT:
            new_head = {'x': self.coords[HEAD]['x'] - 1, 'y': self.coords[HEAD]['y']}
            self.tongue_coords = [
                {'x': self.coords[HEAD]['x'] - 2, 'y': self.coords[HEAD]['y']},
                {'x': self.coords[HEAD]['x'] - 3, 'y': self.coords[HEAD]['y']}
            ]
        elif self.direction == RIGHT:
            new_head = {'x': self.coords[HEAD]['x'] + 1, 'y': self.coords[HEAD]['y']}
            self.tongue_coords = [
                {'x': self.coords[HEAD]['x'] + 2, 'y': self.coords[HEAD]['y']},
                {'x': self.coords[HEAD]['x'] + 3, 'y': self.coords[HEAD]['y']}
            ]

        self.coords.insert(0, new_head)


NUM_APPLES = 3
FPS = 10
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
PINK      = (255, 150, 205)
BLUE      = (  0,   0, 255)
DARKBLUE  = (  0,   0, 155)
GREEN     = (  0, 255,   0)
DARKGREEN = (  0, 155,   0)
DARKGRAY  = ( 40,  40,  40)
GRAY      = ( 75,  75,  75)
YELLOW    = (255, 255,   0)
BROWN     = (140,  95,  30)
BGCOLOR = BLACK

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

HEAD = 0  # syntactic sugar: index of the worm's head


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
            name='Green Worm',
            inner_color=GREEN,
            outline_color=DARKGREEN,
            start_direction=UP,
            start_coord=(6, CELLHEIGHT - 7),
            controls={'left': K_a, 'right': K_d, 'up': K_w, 'down': K_s, 'bite': K_LSHIFT}
        )

        w2 = Worm(
            name='Blue Worm',
            inner_color=BLUE,
            outline_color=DARKBLUE,
            start_direction=DOWN,
            start_coord=(CELLWIDTH - 7, 6),
            controls={'left': K_LEFT, 'right': K_RIGHT, 'up': K_UP, 'down': K_DOWN, 'bite': K_RSHIFT}
        )

        worms = [w1, w2]
        winner = runGame(worms)
        showGameOverScreen(winner)


def runGame(worms):
    time_alive = 0
    stone_coords = []

    # Initialize list of random apples
    apples = []
    for i in range(NUM_APPLES):
        apples.append(getRandomLocation())

    while True:  # main game loop
        for event in pygame.event.get():  # event handling loop
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                # if the worm is alive, get user input for controlling the worm
                for w in worms:
                    if w.alive:
                        w.control_worm(event.key)

        num_dead_worms = 0
        for w in worms:
            # check if worm has been bitten and add stone walls accordingly
            if w.alive:
                new_stones = w.check_bitten(worms)
                if new_stones is not None:
                    stone_coords += new_stones

            # check if worm has died and add stone walls accordingly
            if w.alive:
                new_stones = w.check_death(worms, stone_coords)
                if new_stones is not None:
                    stone_coords += new_stones

            if w.alive:
                w.check_grow(apples)  # check if worm has eaten an apple
                w.change_worm_head()  # re-draw head to render movement

                # if worm uses bite ability, then it becomes a zombie for 8 seconds
                if w.zombie and w.zombie_time > 8000:
                    w.zombie = False
                    w.zombie_time = 0

                # display biting animation for 250 ms
                if w.biting and w.biting_time > 250:
                    w.biting = False
                    w.biting_time = 0
            else:
                num_dead_worms += 1

        # keeps track of time each worm is alive for extra points
        if time_alive >= 1000:
            for w in worms:
                if w.alive and not w.zombie:  # no points for time alive if using zombie ability - ZOMBIES AREN'T ALIVE!
                    w.life_duration += 1
            time_alive = 0

        # end game if all worms are dead
        if num_dead_worms == len(worms):
            print('Game Over!')

            # worm with higher score is the winner
            winner = None
            high_score = 0
            for w in worms:
                score = (w.size_at_death * 100) + (w.life_duration * 5)
                if score > high_score:
                    winner = w
                    high_score = score
            print(f"{winner} Wins!")

            # update last frame to turn the last dying worm into stone and show the correct final scores
            DISPLAYSURF.fill(BGCOLOR)
            drawGrid()
            for stone in stone_coords:
                draw_stone(stone)
            drawScore(worms)
            pygame.display.update()
            return winner

        DISPLAYSURF.fill(BGCOLOR)
        drawGrid()
        for stone in stone_coords:
            draw_stone(stone)
        for w in worms:
            drawWorm(w)
            if w.biting:
                drawTongue(w)
        for apple in apples:
            drawApple(apple)
        drawScore(worms)
        pygame.display.update()
        ms_per_frame = FPSCLOCK.tick(FPS)
        time_alive += ms_per_frame
        for w in worms:
            if w.zombie and w.alive:
                w.zombie_time += ms_per_frame
            if w.biting and w.alive:
                w.biting_time += ms_per_frame


def draw_stone(stone):
        x = stone['x'] * CELLSIZE
        y = stone['y'] * CELLSIZE
        outline_stone_rect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, DARKGRAY, outline_stone_rect)
        inner_stone_rect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
        pygame.draw.rect(DISPLAYSURF, GRAY, inner_stone_rect)


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


def showGameOverScreen(winner):
    gameOverFont = pygame.font.Font('freesansbold.ttf', 100)
    gameSurf = gameOverFont.render('Game', True, WHITE)
    overSurf = gameOverFont.render('Over', True, WHITE)
    gameRect = gameSurf.get_rect()
    overRect = overSurf.get_rect()
    gameRect.midtop = (math.floor(WINDOWWIDTH / 2), 10)
    overRect.midtop = (math.floor(WINDOWWIDTH / 2), gameRect.height + 10 + 25)

    winner_surf = gameOverFont.render(f'{winner} Wins!', True, WHITE)
    winner_rect = winner_surf.get_rect()
    winner_rect.midbottom = (math.floor(WINDOWWIDTH / 2), WINDOWHEIGHT - 10)

    DISPLAYSURF.blit(gameSurf, gameRect)
    DISPLAYSURF.blit(overSurf, overRect)
    DISPLAYSURF.blit(winner_surf, winner_rect)
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
    for w in worms:
        # Scoring: 100pts per apple eaten, 5pts per second alive
        if w.alive:
            score = (len(w.coords) * 100) + (w.life_duration * 5)
        else:
            score = (w.size_at_death * 100) + (w.life_duration * 5)
        scoreSurf = BASICFONT.render(f'{w} Score: {score}', True, WHITE)
        scoreRect = scoreSurf.get_rect()
        scoreRect.topleft = (WINDOWWIDTH - 260, prev_y_location + 25)
        prev_y_location += 25
        DISPLAYSURF.blit(scoreSurf, scoreRect)


def drawWorm(worm):
    if worm.zombie:
        outline_color = BROWN
    else:
        outline_color = worm.outline_color
    for coord in worm.coords:
        x = coord['x'] * CELLSIZE
        y = coord['y'] * CELLSIZE
        wormSegmentRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, outline_color, wormSegmentRect)
        wormInnerSegmentRect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
        pygame.draw.rect(DISPLAYSURF, worm.inner_color, wormInnerSegmentRect)


def drawTongue(worm):
    for coord in worm.tongue_coords:
        if worm.direction == UP or worm.direction == DOWN:
            x = coord['x'] * CELLSIZE + (CELLSIZE/4)
            y = coord['y'] * CELLSIZE
            tongue_rect = pygame.Rect(x, y, CELLSIZE/2, CELLSIZE)
            pygame.draw.rect(DISPLAYSURF, PINK, tongue_rect)
        elif worm.direction == RIGHT or worm.direction == LEFT:
            x = coord['x'] * CELLSIZE
            y = coord['y'] * CELLSIZE + (CELLSIZE/4)
            tongue_rect = pygame.Rect(x, y, CELLSIZE, CELLSIZE/2)
            pygame.draw.rect(DISPLAYSURF, PINK, tongue_rect)


def drawApple(coord):
    x = coord['x'] * CELLSIZE
    y = coord['y'] * CELLSIZE
    xcenter = coord['x'] * CELLSIZE + math.floor(CELLSIZE/2)
    ycenter = coord['y'] * CELLSIZE + math.floor(CELLSIZE/2)
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