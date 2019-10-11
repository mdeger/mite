# tool to calculate the density of bassoon reeds
# using this device:
# https://www.georgrieger.com/en/density-determination-instrument/dichtebestimmungsgeraet-heinrich-fuer-rohrholz.html
#

n = 1
print("\n\n\n\n\n\n")

while True:
    print("\n--------------------------------\n")
    print("density computation number "+str(n)+": \n")

    A = float( input('A = ') )
    B = float( input('B = ') )

    dens = A / (A+abs(B))

    print("density = " + str(dens))
    n += 1

