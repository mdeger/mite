# tool to calculate the density of bassoon reeds
# using this device:
# https://www.georgrieger.com/en/density-determination-instrument/dichtebestimmungsgeraet-heinrich-fuer-rohrholz.html
#

import numpy

n = 1
print("\n\n\n\n\n\n")

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

    print("density = " + str( numpy.round( dens, decimals=2 )))
    n += 1

