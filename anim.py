import numpy
import sys
import solar_sys

import pygame
from pygame.locals import *

##################################GLOBAL VARS############################################

#POSITION AND CENTRALIZATION ------------------------------------------------------------
SCREEN_SIZE = ( 1200 , 800 )
TILE_SIZE   = 5
CENTER = None  #centralize always at this position

# COLOR PALLETE -------------------------------------------------------------------------
BLACK = ( 0  , 0  , 0  )
WHITE = ( 255, 255, 255)

# MOTION --------------------------------------------------------------------------------
SPEED     = 1
MAX_SPEED = 10
MIN_SPEED = 0 # paused

################################## MOTION FUNCTIONS #####################################

def set_center( pos ):

    global CENTER
    CENTER = min( solar_sys.TOTAL , pos )

def center_at_most_massive( ):

    _ , _ , rs = solar_sys.get_elems( )
    pos = numpy.argmax( rs )
    set_center( pos )

def move( ):
    for i in range( SPEED ):
        solar_sys._move( )

def set_speed( key ):

    global SPEED
    if key == K_UP:
        SPEED = min( SPEED + 1 , MAX_SPEED )
    elif key == K_DOWN:
        SPEED = max( SPEED - 1 , MIN_SPEED )

################################## DRAWING FUNCTION #####################################

def draw_planets( surf ):

    cx , cy = SCREEN_SIZE
    xs , ys , rs = solar_sys.get_elems( )
    for x , y , r in zip( xs , ys , rs ):

        true_x = cx/2 + TILE_SIZE*( x - xs[ CENTER ] )
        true_y = cy/2 + TILE_SIZE*( y - ys[ CENTER ] )
        true_r =        TILE_SIZE*r

        pygame.draw.circle( surf , BLACK , ( true_x , true_y ) , true_r )

################################## TEST FUNC ############################################

def test2( ):

    pygame.init()
    disp = pygame.display.set_mode( SCREEN_SIZE )
    solar_sys.add_elem( ( 0 , 0 ) , 25 , ( 0 , 0 ) )
    solar_sys.add_elem( ( 0 , 30 ) , 1 , ( 1 , 0 ) )

    center_at_most_massive()
    while True:
        disp.fill( WHITE )
        draw_planets( disp )
        move()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYUP:
                set_speed( event.key )
        pygame.display.update()

def test1( ):

    pygame.init()
    disp = pygame.display.set_mode( SCREEN_SIZE )
    solar_sys.add_elem( ( 0 , 0 ) , 25 , ( 0 , 0 ) )
    solar_sys.add_elem( ( 0 , 10 ) , 1 , ( 1 , 0 ) )
    solar_sys.add_elem( ( 0 , 20 ) , 1 , ( 1 , 0 ) )
    solar_sys.add_elem( ( 0 , 30 ) , 1 , ( 1 , 0 ) )
    solar_sys.add_elem( ( 0 , 40 ) , 1 , ( 1 , 0 ) )

    center_at_most_massive()
    while True:
        disp.fill( WHITE )
        draw_planets( disp )
        move()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.update()

################################## MAIN FUNC ############################################
if __name__ == "__main__":
    test2()
