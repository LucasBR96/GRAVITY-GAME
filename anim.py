import numpy
import sys
import solar_sys
import random

import time

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
RED   = ( 255 , 0 , 0 )

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

    CX , CY = 0 , 0 
    if not( CENTER is None ):
        CX = xs[ CENTER ]
        CY = ys[ CENTER ]

    for x , y , r in zip( xs , ys , rs ):

        true_x = cx/2 + TILE_SIZE*( x - CX )
        true_y = cy/2 + TILE_SIZE*( y - CY )
        true_r =        TILE_SIZE*r

        pygame.draw.circle( surf , BLACK , ( true_x , true_y ) , true_r )

################################## TEST FUNC ############################################

def test3( ):

    pygame.init()
    disp = pygame.display.set_mode( SCREEN_SIZE )
    
    # RANDOM GALAXY ------------------------------------------------

    r_min , dr  = 10 , 40 
    full_circle = 2*numpy.pi
    starting_pos = set( )
    while len( starting_pos ) < 100:

        # polar coordinates-----------------------------------------
        r     = r_min + random.random()*dr
        theta = random.random()*full_circle
        starting_pos.add( ( r , theta ) )
    
    for r , theta in starting_pos:

        a = numpy.cos( theta )
        b = numpy.sin( theta )
        pos = ( r*a , r*b )

        a , b = -b , a  
        s = .1*r/r_min
        vel = ( s*a , s*b )

        solar_sys.add_elem( pos , 1 , vel )
    
    # ---------------------------------------------------------------

    count = 0
    max_count = 100
    tsum_ = 0
    while True:
        t0 = time.time()

        disp.fill( WHITE )
        draw_planets( disp )
        move()

        # PAINTING COLISIONS IN RED ------------------------------------------------

        cx , cy = SCREEN_SIZE
        xs , ys , rs = solar_sys.get_elems( )
        col = solar_sys.test_colision()
        for i in col:

            true_x = cx/2 + TILE_SIZE*( xs[ i ] )
            true_y = cy/2 + TILE_SIZE*( ys[ i ] )
            true_r =        TILE_SIZE*rs[ i ]

            pygame.draw.circle( disp , RED , ( true_x , true_y ) , true_r )
        
        # ----------------------------------------------------------------------

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYUP:
                set_speed( event.key )
        pygame.display.update()

        tsum_ += time.time( ) - t0
        count = ( count + 1 )%max_count
        if not count:
            print( max_count/tsum_ )
            tsum_ = 0

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
    test3()
