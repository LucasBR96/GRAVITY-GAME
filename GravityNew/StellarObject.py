import numpy
from collections import namedtuple

planet = namedtuple( "planet" , [ "mass" , "x" , "vx" , "y" , "dy" ] )

def planet_list_to_flock( planet_list ):

    condensed_data = zip( *planet_list )
    flock = planet( *[ numpy.array( x ) for x in condensed_data ] )
    return flock

def flock_to_planlst( flock ):

    plnts = zip( flock.mass , flock.x , flock.dx , flock.y , flock.vy )
    plnt_lst = []
    for info in plnts:
        plnt_lst.append( planet( *info ) )
    return plnt_lst

class planet_sys:

    def __init__
