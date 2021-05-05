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
K  = .7 # ELASTIC CONSTANT

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

def remove_elem( pos ):

    global TOTAL

    if pos > TOTAL: return
    TOTAL = max( TOTAL -1 , 0 )

    if pos == TOTAL: return

    swap( pos , TOTAL )

def swap( i , j ):

    XS[ i ] , XS[ j ] = XS[ j ] , XS[ i ]
    YS[ i ] , YS[ j ] = YS[ j ] , YS[ i ]

    V_XS[ i ] , V_XS[ j ] = V_XS[ j ] , V_XS[ i ]
    V_YS[ i ] , V_YS[ j ] = V_YS[ j ] , V_YS[ i ]
    
    MASSES[ i ] , MASSES[ j ] =  MASSES[ i ] , MASSES[ j ]
    RADIUS[ i ] , RADIUS[ j ] =  RADIUS[ j ] , RADIUS[ i ]

def _add_elem( pos , mass , vel ):

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

def _get_elems( ):

    s = slice( TOTAL )
    xs = XS[ s ]
    ys = YS[ s ]
    rs = RADIUS[ s ]
    return xs , ys , rs

def partition( positions ):

    # positions.sort( )
    n = len( positions )
    for i , pos in enumerate( positions ):
        swap( pos , TOTAL - n + i )
    return TOTAL - n

###################### COLISION FUNCTIONS ################################

def collide( i , j ):
    sqr_dist = ( XS[ i ] - XS[ j ] )**2 + ( YS[ i ] - YS[ j ] )**2
    rad_sum  = ( RADIUS[ i ] + RADIUS[ j ] )**2
    return sqr_dist <= rad_sum

def get_collisions():

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
            if collide( i , j ): 
                visited.add( ( i , j ) )

    return visited        
        
def elastict_collision( i , j ):
    
    if not K: return

    # FINDING THE CONTACT POINT -------------------------------------------------------------

    p = i if MASSES[ i ] > MASSES[ j ] else j
    q = j if p == i else i

    xp , yp , rp = XS[ p ] , YS[ p ] , RADIUS[ p ]
    xq , yq , rq = XS[ q ] , YS[ q ] , RADIUS[ q ]

    d_square = ( xp - xq )**2 + ( yp - yq )**2
    r_sum    = rp + rq
    r_diff   = rp - rq
    a = ( r_sum*r_diff + d_square )/( 2*d_square )

    xu = a*( xq - xp ) + xp
    yu = a*( yq - yp ) + yp

    # REPOSITIONING THE BALLS ----------------------------------------------------------------
    dx = xq - xp
    dy = yq - yp
    d = numpy.sqrt( d_square )

    XS[ q ] = xu + rq*( dx/d )
    YS[ q ] = yu + rq*( dy/d )

    XS[ p ] = xu - rp*( dx/d )
    YS[ p ] = yu - rp*( dy/d )
    
    # RECALCULATING SPEEDS ---------------------------------------------------------------------


def merge( i , j ):

    mass_sum = MASSES[ i ] + MASSES[ j ]
    new_x =  ( XS[   i ]*MASSES[ i ] + XS[   j ]*MASSES[ j ] )/mass_sum
    new_y =  ( YS[   i ]*MASSES[ i ] + YS[   j ]*MASSES[ j ] )/mass_sum
    new_vx = ( V_XS[ i ]*MASSES[ i ] + V_XS[ j ]*MASSES[ j ] )/mass_sum
    new_vy = ( V_YS[ i ]*MASSES[ i ] + V_YS[ j ]*MASSES[ j ] )/mass_sum

    return ( new_x , new_y ) , mass_sum , ( new_vx , new_vy )

def _handle_collision( ):
   
    visited = get_collisions()
    if not visited: return

    for i , j in visited:
        elastict_collision( i , j )
    
    if K: return

    to_remove = set( )
    tups = []
    for i , j in visited:
        if i in to_remove or j in to_remove:
            continue

        tups.append( merge( i , j ) )
        to_remove.add( i )
        to_remove.add( j )
        
    
    global TOTAL
    TOTAL = partition( to_remove )
    
    for tup in tups:
        _add_elem( *tup ) 


def _set_elas( val ):

    val = max( val , 0 )
    val = min( val , 1 )

    global K
    K = val
######################## MOTION FUNCTIONS ################################

def remove_main_diag( Mat ):

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

def get_distances( ):

    s = slice( TOTAL )

    xs = XS[ s ].reshape( ( 1 , TOTAL ) )
    dx = xs.T - xs
    dx = remove_main_diag( dx )

    ys = YS[ s ].reshape( ( 1 , TOTAL ) )
    dy = ys.T - ys
    dy = remove_main_diag( dy )

    d = numpy.sqrt( dx**2 + dy**2 )

    return -dx , -dy , d 

def get_mass_product( ):

    s = slice( TOTAL )
    masses = MASSES[ s ].reshape( ( 1 , TOTAL ) )
    prod   = numpy.ones( ( TOTAL , 1 ) )
    masses = remove_main_diag( masses*prod )
    return G*masses

def get_acceleration( ):

    masses      = get_mass_product()
    dx , dy , d = get_distances()

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

    acx , acy = get_acceleration()
    V_XS[ s ] += acx*DT
    V_YS[ s ] += acy*DT

######################## TESTS FUNCTIONS ################################

def test1( ):

    _add_elem( ( 0 , 0 ) , 5 , ( 0 , 0 ) )
    _add_elem( ( 0 , 1 ) , 5 , ( 0 , 0 ) )
    _add_elem( ( 1 , 0 ) , 5 , ( 0 , 0 ) )

    acm_x , acm_y = get_acceleration( )
    for acx , acy in zip( acm_x , acm_y ):
        print( acx , acy )

def test2( ):

    _add_elem( ( 0 , 0 ) , 25 , ( 0 , 0 ) )
    _add_elem( ( 1 , 0 ) , 1 , ( 10 , 0 ) )
    # add_elem( ( 1 , 0 ) , 1 , ( 0 , 0 ) )

    for i in range( 10**4 ):
        _move()
        if i%( 10**3 ): continue
        print( XS[ 0 ] , YS[ 0 ] )

if __name__ == "__main__":
    test2()