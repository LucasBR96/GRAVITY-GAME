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


def add_elem( pos , mass , vel ):

    global TOTAL
    if TOTAL >= MAXITEMS: return

    ( x , y )   = pos
    XS[ TOTAL ] = x
    YS[ TOTAL ] = y

    MASSES[ TOTAL ] = mass

    ( vx , vy )   = vel
    V_XS[ TOTAL ] = vx
    V_YS[ TOTAL ] = vy

    TOTAL += 1

def get_elems( ):

    s = slice( TOTAL )
    xs = XS[ s ]
    ys = YS[ s ]
    rs = MIN_R + FOO( MASSES[ s ] )
    return xs , ys , rs

###################### COLISION FUNCTIONS ################################

def test_colision():

    idx = list( range( TOTAL ) )
    idx.sort( key = lambda x: XS[ x ] )

    radius = numpy.array( [ MIN_R + FOO( MASSES[ i ] ) for i in range( TOTAL ) ] ) 

    visited = set()
    for i in range( TOTAL - 1 ):
        pos = idx[ i ]
        r = radius[ pos ]
        for j in range( i + 1, TOTAL ):
            pos_prime = idx[ j ]
            r_prime = radius[ pos ]

            if XS[ pos_prime ] - r_prime > XS[ pos ] + r:
                break
            
            dx = XS[ pos_prime ] - XS[ pos ]
            dy = YS[ pos_prime ] - YS[ pos ]
            if ( dx**2 ) + ( dy**2 ) < ( r + r_prime )**2:
                # visited.add( ( i , j ) )
                visited.add( pos )
                visited.add( pos_prime )
                break
    return visited

def handle_collision():
    pass



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