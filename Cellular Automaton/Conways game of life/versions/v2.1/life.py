import os, time, random


# ========================================================================= #
# ------------------------------- FUNCTIONS ------------------------------- #
# ========================================================================= #

# Compute the cell's next stage
def nextGen(y: int, x: int) -> int:
    alive = 0
    for i in range(4):
        index1 = i * 2
        index2 = index1 + 1
        b1 = int([y + neighbors[index1][0], x + neighbors[index1][1]] in livingCells)
        b2 = int([y + neighbors[index2][0], x + neighbors[index2][1]] in livingCells)
        alive += ((b1 & b2) << 1) | (b1 ^ b2)
    return int((alive == 3) or (([y,x] in livingCells) and alive == 2))


# Apply nextGen() function to every cell within boundary and also update to its next state
def update():
    liminalCells = []
    investigated = []
    for y, x in livingCells:
        if [y, x] not in investigated:
            investigated.append([y, x])
            if nextGen(y,x):
                liminalCells.append([y,x])

        for i, j in neighbors:
            if [y + i, x + j] not in investigated:
                investigated.append([y + i, x + j])
                if nextGen(y + i, x + j):
                    liminalCells.append([y + i, x + j])

    for y, x in investigated:
        if ([y, x] in liminalCells) and ([y, x] not in livingCells):
            livingCells.append([y, x])
        elif ([y, x] not in liminalCells) and ([y, x] in livingCells):
            livingCells.remove([y, x])

        
# Display the world at each generation
def render():
    global lowY, highY, lowX, highX
    y_axis, x_axis = zip(*livingCells)
    minY, maxY, minX, maxX = min(y_axis), max(y_axis),min(x_axis), max(x_axis)
    # Use the lowest x,y and highest x,y value obtained to keep world from ever shrinking
    if minY < lowY:
        lowY = minY
    if minX < lowX:
        lowX = minX
    if maxY > highY:
        highY = maxY
    if maxX > highX:
        highX = maxX
    y_range, x_range = range(lowY, highY+2), range(lowX, highX+2)
    for y in y_range:
        print(''.join('⬜' if [y,x] in livingCells else '⬛' for x in x_range))


# ========================================================================= #
# ------------------------------ MAIN DRIVER ------------------------------ #
# ========================================================================= #

# Initialising variables/constants
neighbors = ((1, -1), (1, 0), 
             (1, 1), (0, 1), 
             (-1, 1), (-1, 0), 
             (-1, -1), (0, -1))
livingCells = []
lowY, highY, lowX, highX = 0, 0, 0, 0

# Loading pattern
default = input("Use (d)efaults or press anything else to make random patterns: ")
if default == 'd':
    from decoder import pattern
    pattern(livingCells)
else:
    for y in range(1, 19):
        for x in range(1, 19):
            if random.randint(0,1):
                livingCells.append([y,x])

# Displaying the pattern
render()
time.sleep(5)
os.system('cls')

# Start the evolution
while True:
    render()
    update()
    time.sleep(0.1)
    os.system('cls')