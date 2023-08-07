# tool to calculate the density of bassoon reeds
# using this device:
# https://www.georgrieger.com/en/density-determination-instrument/dichtebestimmungsgeraet-heinrich-fuer-rohrholz.html
#

import numpy

n = 1
stats = {}
print("\n\n\n\n\n\n")


def print_stats():
    """print running density statistic"""
    keys = stats.keys()
    keys.sort()
    print('\nrunning density statistics:')
    for k in keys:
        nk = stats[k]
        p = int( round( float( nk ) / n * 100., 0 ) )
        print( str(k)+'     '+str(nk)+'     '+str(p)+'%' )


while True:
    print("\n--------------------------------\n")
    
    print("density computation number "+str(n)+": \n")

    try:
        A = input('A = ')
        B = input('B = ')
    except:
        print("[ERROR] could not register A or B value. Make sure to enter valid numbers!")
        continue
        
    try:
        dens = float( A ) / ( float( A ) + abs( float( B ) ) )
    except:
        print("[ERROR] could not compute density. Make sure to enter valid numbers!")
        continue

    density = numpy.round( dens, decimals=2 )
    print("density = " + str( density))

    "register in running statistics dictionary and print statistics"
    if density in stats.keys():
        stats[density] += 1
    else:
        stats[density] = 1
    print_stats()
    
    n += 1

