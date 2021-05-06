import pygame
from pygame.locals import *

# COLORS -----------------------------------------------------------------------------

BLACK = ( 0  , 0  , 0   )
WHITE = ( 255, 255, 255 )
GREY = ( 125, 125, 125 )
RED   = ( 255 , 0 , 0 )

BACKGROUND  = WHITE
FOREGROUND  = BLACK

def draw_new_pos( surf, x , y , r , arrow_x , arrow_y ):

    pygame.draw.circle( surf , GREY , ( x , y ) , r )
    if ( arrow_x is None ) or ( arrow_y is None ):
        return
    
    pygame.draw.line( surf , FOREGROUND , ( x , y ) , ( arrow_x , arrow_y ) )

def draw_existing_planets( surf , xs , ys , rs , shape ):
    
    x , y = shape
    x_lim_inf = -rs
    x_lim_sup = x + rs
    y_lim_inf = -rs
    y_lim_sup = y + rs

    n = len( xs )
    for i in range( n ):
        a = x_lim_inf[ i ] < xs[ i ] < x_lim_sup[ i ]
        b = y_lim_inf[ i ] < ys[ i ] < y_lim_sup[ i ]

        if a and b: # if don't, don't bother drawing.
            pygame.draw.circle( surf , FOREGROUND , ( xs[ i ] , ys[ i ] ) , rs[ i ] )