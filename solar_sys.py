import numpy
import time
from itertools import product ,combinations
from sys import maxsize
######################## GLOBAL VARS ####################################

#GRAVITATIONAL PROPERTIES OF THE SYSTEM ---------------------------------
G     = 20          # UNIVERSAL CONSTANT
MIN_R = 1          # PIXELS
FOO   = numpy.log10
R_FUN = lambda x: MIN_R + FOO( x )

# MOTION properties ---------------------------------------
DT = .01

# EVERY PLANET AND HER PROPERTIES ---------------------------------------
TOTAL = 0
MAXITEMS = 10**3
XS     = numpy.zeros( MAXITEMS )
YS     = numpy.zeros( MAXITEMS )
V_XS   = numpy.zeros( MAXITEMS )
V_YS   = numpy.zeros( MAXITEMS )
MASSES = numpy.zeros( MAXITEMS )
RADIUS = numpy.zeros( MAXITEMS )

######################## ELEMENT MANIPUALTION FUNCTIONS ###############################

def _remove_elem( pos ):

    global TOTAL

    if pos > TOTAL: return
    TOTAL = max( TOTAL -1 , 0 )

    if pos == TOTAL: return

    _swap( pos , TOTAL )

def _swap( i , j ):

    XS[ i ] , XS[ j ] = XS[ j ] , XS[ i ]
    YS[ i ] , YS[ j ] = YS[ j ] , YS[ i ]

    V_XS[ i ] , V_XS[ j ] = V_XS[ j ] , V_XS[ i ]
    V_YS[ i ] , V_YS[ j ] = V_YS[ j ] , V_YS[ i ]
    
    MASSES[ i ] , MASSES[ j ] =  MASSES[ i ] , MASSES[ j ]
    RADIUS[ i ] , RADIUS[ j ] =  RADIUS[ j ] , RADIUS[ i ]


###################### COLISION FUNCTIONS ################################

def _collide( i , j ):
    sqr_dist = ( XS[ i ] - XS[ j ] )**2 + ( YS[ i ] - YS[ j ] )**2
    rad_sum  = ( RADIUS[ i ] + RADIUS[ j ] )**2
    return sqr_dist <= rad_sum

def _get_collisions():

    foo = lambda x: XS[ x ] - RADIUS[ x ]
    idx = list( range( TOTAL ) )
    idx.sort( key = foo )

    collision_groups = []
    i , lim = 0 , -maxsize
    while i < TOTAL:

        pos = idx[ i ]
        current_group = [ pos ]
        if XS[ pos ] - RADIUS[ pos ] < lim:
            current_group = collision_groups.pop() + current_group
        collision_groups.append( current_group )
        
        lim = XS[ pos ] + RADIUS[ pos ]
        i += 1
    
    visited = set()
    for group in collision_groups:
        if len( group ) == 1: continue 
        for i , j in combinations( group , 2 ):
            if _collide( i , j ): 
                visited.add( ( i , j ) )

    return visited        

def merge( i , j ):

    mass_sum = MASSES[ i ] + MASSES[ j ]
    new_x =  ( XS[   i ]*MASSES[ i ] + XS[   j ]*MASSES[ j ] )/mass_sum
    new_y =  ( YS[   i ]*MASSES[ i ] + YS[   j ]*MASSES[ j ] )/mass_sum
    new_vx = ( V_XS[ i ]*MASSES[ i ] + V_XS[ j ]*MASSES[ j ] )/mass_sum
    new_vy = ( V_YS[ i ]*MASSES[ i ] + V_YS[ j ]*MASSES[ j ] )/mass_sum

    return ( new_x , new_y ) , mass_sum , ( new_vx , new_vy )

def _handle_collision( ):
   
    visited = _get_collisions()
    handled = set()
    
    for i , j in visited:
        if i in handled or j in handled:
            continue
        handled.add( i )
        handled.add( j )

        tup = merge( i , j )
        add_elem( *tup )
    
    for i in handled:
        _remove_elem( i )

######################## MOTION FUNCTIONS ################################

def _remove_main_diag( Mat ):

    m , n = Mat.shape
    if m != n: 
        raise ValueError ( "square matrix only" )

    Mat_prime = numpy.zeros( ( m - 1 )*m )
    k = 0 
    for i , j in product( range( m ) , range( n ) ):
        if i == j: continue
        Mat_prime[ k ] = Mat[ i , j ]
        k += 1
    
    return Mat_prime.reshape( ( m , m - 1 ) )

def _get_distances( ):

    s = slice( TOTAL )

    xs = XS[ s ].reshape( ( 1 , TOTAL ) )
    dx = xs.T - xs
    dx = _remove_main_diag( dx )

    ys = YS[ s ].reshape( ( 1 , TOTAL ) )
    dy = ys.T - ys
    dy = _remove_main_diag( dy )

    d = numpy.sqrt( dx**2 + dy**2 )

    return -dx , -dy , d 

def _get_mass_product( ):

    s = slice( TOTAL )
    masses = MASSES[ s ].reshape( ( 1 , TOTAL ) )
    prod   = numpy.ones( ( TOTAL , 1 ) )
    masses = _remove_main_diag( masses*prod )
    return G*masses

def _get_acceleration( ):

    masses      = _get_mass_product()
    dx , dy , d = _get_distances()

    ratio_x = dx/( d**3 )
    acm_x   = ( masses*ratio_x ).sum( axis = 1 , keepdims = False )

    ratio_y = dy/( d**3 )
    acm_y   = ( masses*ratio_y ).sum( axis = 1 , keepdims = False )

    return acm_x , acm_y

def _move(  ):

    s = slice( TOTAL )
    vx = V_XS[ s ]*DT 
    XS[ s ] += vx

    vy = V_YS[ s ]*DT
    YS[ s ] += vy 

    acx , acy = _get_acceleration()
    V_XS[ s ] += acx*DT
    V_YS[ s ] += acy*DT

######################## FOCUS FUNCTIONS ################################

CENTER          = ( 0 , 0 )
FOCUS           = 0
CENTER_ON_FOCUS = False

def move_center( dx , dy ):

    global CENTER , CENTER_ON_FOCUS

    cx , cy = CENTER
    cx += dx
    cy += dy
    CENTER = ( cx , cy )

    CENTER_ON_FOCUS = False

def focus_on_next( ):

    global FOCUS , CENTER_ON_FOCUS

    FOCUS = ( FOCUS + 1 )%TOTAL
    CENTER_ON_FOCUS = True

def focus_on_previous( ):

    global FOCUS , CENTER_ON_FOCUS

    FOCUS = ( FOCUS - 1 )%TOTAL
    CENTER_ON_FOCUS = True

def focus_on_massive( ):

    global FOCUS , CENTER_ON_FOCUS

    s = slice( TOTAL )
    m = MASSES[ s ]
    FOCUS = numpy.argmax( m )
    CENTER_ON_FOCUS = True

######################## SPEED FUNCTIONS ################################

SPEED     = 1
MIN_SPEED = 1
MAX_SPEED = 10

PAUSED = False

def add_speed( ):

    if PAUSED: return

    global SPEED
    SPEED = min( MAX_SPEED , SPEED + 1 )

def remove_speed( ):

    if PAUSED: return

    global SPEED
    SPEED = max( MIN_SPEED , SPEED - 1 )
    
def flip_pause( ):

    global PAUSED
    PAUSED = not PAUSED

def update( ):

    if PAUSED: return
    for i in range( SPEED ):
        _move()
        _handle_collision( )

##################### DATA EXCHANGE WITh OTHER FILES ####################

def add_elem( pos , mass , vel ):

    global TOTAL
    if TOTAL >= MAXITEMS: return

    ( x , y )   = pos
    XS[ TOTAL ] = x
    YS[ TOTAL ] = y

    ( vx , vy )   = vel
    V_XS[ TOTAL ] = vx
    V_YS[ TOTAL ] = vy

    MASSES[ TOTAL ] = mass
    RADIUS[ TOTAL ] = R_FUN( mass )
    TOTAL += 1

def get_elems( ):

    global CENTER
    if CENTER_ON_FOCUS:
        CENTER = ( XS[ FOCUS ] , YS[ FOCUS ] )

    cx , cy = CENTER
    s = slice( TOTAL )
    xs = XS[ s ] - cx
    ys = YS[ s ] - cy
    rs = RADIUS[ s ]
    return xs , ys , rs

######################## TESTS FUNCTIONS ################################

def test1( ):

    add_elem( ( 0 , 0 ) , 5 , ( 0 , 0 ) )
    add_elem( ( 0 , 1 ) , 5 , ( 0 , 0 ) )
    add_elem( ( 1 , 0 ) , 5 , ( 0 , 0 ) )

    acm_x , acm_y = _get_acceleration( )
    for acx , acy in zip( acm_x , acm_y ):
        print( acx , acy )

def test2( ):

    add_elem( ( 0 , 0 ) , 25 , ( 0 , 0 ) )
    add_elem( ( 1 , 0 ) , 1 , ( 10 , 0 ) )
    # add_elem( ( 1 , 0 ) , 1 , ( 0 , 0 ) )

    for i in range( 10**4 ):
        _move()
        if i%( 10**3 ): continue
        print( XS[ 0 ] , YS[ 0 ] )

if __name__ == "__main__":
    test2()