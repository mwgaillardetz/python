# <.SYNOPSIS - This program generates a random name from a self-provided txt file of entries. 
# To run this successfully, you need to provide your own .txt file containing names, without commas,
# and each on their own line. *Fun fact, this was how I named my first son :)

import random
a_file = open("boyNames.txt", "r")
boyNames = [(line.strip()).split() for line in a_file]
a_file.close()

while True:
    name = random.choice(boyNames)
    x = input('Press enter for a random name. Enter d when done.')
    if x == 'd':
        break
    print (random.choice(name))
