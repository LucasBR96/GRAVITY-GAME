import numpy
import time
from itertools import product

######################## GLOBAL VARS ####################################

#GRAVITATIONAL PROPERTIES OF THE SYSTEM ---------------------------------
G     = 1          # UNIVERSAL CONSTANT
MIN_R = 1          # PIXELS
FOO   = numpy.log10 # R = MIN_R + FOO( M )

# MOTION properties ---------------------------------------
DT    = .01

# EVERY PLANET AND HER PROPERTIES ---------------------------------------
TOTAL = 0
MAXITEMS = 10**3
XS     = numpy.zeros( MAXITEMS )
YS     = numpy.zeros( MAXITEMS )
V_XS   = numpy.zeros( MAXITEMS )
V_YS   = numpy.zeros( MAXITEMS )
MASSES = numpy.zeros( MAXITEMS )
RADIUS = numpy.zeros( MAXITEMS )

######################## OVERALL FUNCTIONS ###############################

def _move(  ):

    s = slice( TOTAL )
    vx = V_XS[ s ]*DT 
    XS[ s ] += vx

    vy = V_YS[ s ]*DT
    YS[ s ] += vy 

    acx , acy = get_acceleration()
    V_XS[ s ] += acx*DT
    V_YS[ s ] += acy*DT

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
    RADIUS[ i ] , RADIUS[ j ] =  MASSES[ j ] , MASSES[ i ]

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
    RADIUS[ TOTAL ] = MIN_R + FOO( mass )
    TOTAL += 1

def get_elems( ):

    s = slice( TOTAL )
    xs = XS[ s ]
    ys = YS[ s ]
    rs = RADIUS[ s ]
    return xs , ys , rs

###################### COLISION FUNCTIONS ################################

def colide( i , j ):
    sqr_dist = ( XS[ i ] - XS[ j ] )**2 + ( YS[ i ] - YS[ j ] )**2
    rad_sum  = ( RADIUS[ i ] + RADIUS[ j ] )**2
    return sqr_dist < rad_sum

def get_colisions():

    idx = list( range( TOTAL ) )
    idx.sort( key = lambda x: XS[ x ] - RADIUS[ x ] )

    visited = set()
    mid = 0
    while mid < TOTAL - 1:

        i = idx[ mid ]
        j = idx[ mid + 1 ]

        if colide( i , j ):
            visited.add( i )
            visited.add( j )
        
        mid += 1

    return visited        
        
def handle_collision( col_set ):

    idx = list( col_set )
    idx.sort( key = lambda x: XS[ x ] - RADIUS[ x ] )
   
    to_remove = set()
    root , stem = -1 , -1
    for x in idx:

        if root == -1:
            root = x
            continue
        stem = x

        if colide( root , stem ):
            merge( root , stem )
            to_remove.add( stem )  
        else:
            root = stem

    for i in to_remove:
        remove_elem( i )    

def merge( i , j ):

    k1 , k2 = i , j
    mass_sum = MASSES[ k1 ] + MASSES[ k2 ]

    new_x =  ( XS[ k2 ]*MASSES[ k2 ] + XS[ k1 ]*MASSES[ k1 ] )/mass_sum
    new_y =  ( YS[ k2 ]*MASSES[ k2 ] + YS[ k1 ]*MASSES[ k1 ] )/mass_sum
    new_vx = ( V_XS[ k2 ]*MASSES[ k2 ] + V_XS[ k1 ]*MASSES[ k1 ] )/mass_sum
    new_vy = ( V_YS[ k2 ]*MASSES[ k2 ] + V_YS[ k1 ]*MASSES[ k1 ] )/mass_sum

    MASSES[ k1 ] = mass_sum
    RADIUS[ k1 ] = MIN_R + FOO( mass_sum )
    XS[ k1 ]   = new_x 
    YS[ k1 ]   = new_y 
    V_XS[ k1 ] = new_vx 
    V_YS[ k1 ] = new_vy

    return k2 
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

######################## TESTS FUNCTIONS ################################

def test1( ):

    add_elem( ( 0 , 0 ) , 5 , ( 0 , 0 ) )
    add_elem( ( 0 , 1 ) , 5 , ( 0 , 0 ) )
    add_elem( ( 1 , 0 ) , 5 , ( 0 , 0 ) )

    acm_x , acm_y = get_acceleration( )
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