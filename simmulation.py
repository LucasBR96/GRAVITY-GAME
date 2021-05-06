import solar_sys
import drawing_functions

import pygame
from pygame.locals import *

import sys

# SCREEN STUFF ------------------------------------------------------------------------
SCREEN_SIZE = ( 1200 , 800 )
DISPLAYSURF = pygame.display.set_mode( SCREEN_SIZE )
TILE_SIZE   = 2

SCREEN_MOTION = False
MOTION_DIRECT = None

def move_screen( ):

    if not SCREEN_MOTION:
        return
    
    dx , dy = MOTION_DIRECT
    solar_sys.move_center( dx , dy )


def get_screen( ):

    DISPLAYSURF.fill( drawing_functions.BACKGROUND )
    move_screen( )

    # NEW POSSIBLE PLANET -----------------------------------------------------------
    set_birth_pos()
    x = BIRTH_POSX
    y = BIRTH_POSY
    r = solar_sys.R_FUN( NEW_M )*TILE_SIZE

    arrow_x , arrow_y = None , None
    if MOUSE_HOLD:  
        arrow_x , arrow_y = MOUSE_X , MOUSE_Y
    drawing_functions.draw_new_pos( DISPLAYSURF, x , y , r , arrow_x , arrow_y )

    # HANDLING EXISTING PLANETS ---------------------------------------------------
    x  ,  y = SCREEN_SIZE

    if solar_sys.TOTAL:
        solar_sys.update()
        xs , ys , rs = solar_sys.get_elems()

        rs = rs*TILE_SIZE
        xs = xs*TILE_SIZE + x/2 
        ys = ys*TILE_SIZE + y/2
        drawing_functions.draw_existing_planets( DISPLAYSURF, xs , ys , rs , ( x , y ) )

#KEYBOARD HANDLING -------------------------------------------------------------------
SPEED_KEYS  = ( K_UP , K_DOWN , K_p )
FOCUS_KEYS  = ( K_LEFT , K_RIGHT , K_m )
SCREEN_KEYS = ( K_w , K_s , K_a , K_d )

def handle_speed( event ):

    if event.type == KEYDOWN: return

    foo = solar_sys.flip_pause
    if event.key == K_UP:
        foo = solar_sys.add_speed
    elif event.key == K_DOWN:
        foo = solar_sys.remove_speed
    
    foo()

def handle_focus( event ):

    if event.type == KEYDOWN: return

    foo = solar_sys.focus_on_massive
    if event.key == K_RIGHT:
        foo = solar_sys.focus_on_next
    elif event.key == K_LEFT:
        foo = solar_sys.focus_on_previous
    
    foo()

def set_motion( event ):

    global SCREEN_MOTION , MOTION_DIRECT

    if event.type == KEYUP:
        SCREEN_MOTION = False
        MOTION_DIRECT = None
        return

    SCREEN_MOTION = True
    dx , dy = 0 , 0
    if   event.key == K_s: dy =  .1
    elif event.key == K_w: dy = -.1
    elif event.key == K_d: dx =  .1
    elif event.key == K_a: dx = -.1

    MOTION_DIRECT = ( dx , dy )

def handle_keyboard_event( event ):

    if not hasattr( event , 'key' ):
        return

    if event.key in SPEED_KEYS:
        handle_speed( event )
    elif event.key in FOCUS_KEYS:
        handle_focus( event )
    elif event.key in SCREEN_KEYS:
        set_motion( event )

#NEW PLANETS -------------------------------------------------------------------------

BIRTH_POSX = 0
BIRTH_POSY = 0

NEW_M = 5
MIN_M = 1
MAX_M = 10**4

def set_birth_pos():

    if MOUSE_HOLD: return

    global BIRTH_POSX , BIRTH_POSY
    BIRTH_POSX = MOUSE_X
    BIRTH_POSY = MOUSE_Y

def release_planet():
    
    global BIRTH_POSX , BIRTH_POSY , NEW_M

    cx , cy = solar_sys.CENTER
    bx , by = BIRTH_POSX , BIRTH_POSY
    x  ,  y = SCREEN_SIZE

    # STARTING POS -------------------------------------------------------------------
    pos_x = cx + ( bx - x/2 )/TILE_SIZE
    pos_y = cy + ( by - y/2 )/TILE_SIZE

    # VELOCITY -----------------------------------------------------------------------
    bx , by = MOUSE_X , MOUSE_Y
    v_x = cx - pos_x + ( bx - x/2 )/( TILE_SIZE )
    v_y = cy - pos_y + ( by - y/2 )/( TILE_SIZE )

    if v_x**2 + v_y**2 < solar_sys.R_FUN( NEW_M )**2:
        v_x , v_y = 0 , 0 # to slow to bother

    # ADDING TO THE POOL AND RESETING VARS -------------------------------------------

    solar_sys.add_elem( ( pos_x , pos_y ) , NEW_M , ( v_x/2 , v_y/2 ) )
    BIRTH_POSX = 0
    BIRTH_POSY = 0
    NEW_M      = 5

def mass_up( ):

    global NEW_M
    NEW_M = min( MAX_M , 2*NEW_M )
    print( NEW_M )

def mass_down( ):

    global NEW_M
    NEW_M = max( MIN_M , NEW_M/2 )
    print( NEW_M )

#MOUSE STATUS -----------------------------------------------------------------------

MOUSE_X = 0
MOUSE_Y = 0
MOUSE_HOLD = False

def valid_mouse_pos( x , y ):
    
    MX , MY = SCREEN_SIZE
    a = ( 0 <= x < MX )
    b = ( 0 <= y < MY )
    return a and b

def set_mouse_pos( x , y ):
    if not valid_mouse_pos( x , y ):
        return
    
    global MOUSE_X , MOUSE_Y
    MOUSE_X = x
    MOUSE_Y = y
    # print( MOUSE_X , MOUSE_Y )


def handle_mouse_event( event ):

    global MOUSE_HOLD

    if event.type == MOUSEMOTION:
        set_mouse_pos( *event.pos )
    elif event.type == MOUSEBUTTONDOWN:
        if event.button == 1:
            MOUSE_HOLD = True
    elif event.type == MOUSEBUTTONUP:
        
        if event.button == 1:   # LEFT BUTTON 
            MOUSE_HOLD = False
            release_planet()
        elif event.button == 4: # WHEEL UP
            mass_up()
        elif event.button == 5: # WHEEL DOWN
            mass_down()

# MAINCODE ----------------------------------------------------------------------------

def main():

    pygame.init()
    while True:
        get_screen( )
        set_birth_pos( )
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
                return
            handle_mouse_event( event )
            handle_keyboard_event( event )

        pygame.display.update()

if __name__ == "__main__":
    main()