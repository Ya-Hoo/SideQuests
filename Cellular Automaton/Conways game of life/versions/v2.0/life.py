import os, time, random


# ========================================================================= #
# ------------------------------- FUNCTIONS ------------------------------- #
# ========================================================================= #

# Create world with dead cells as a 2D array
def worldGen(width: int, height: int) -> list:
    grid = []
    for y in range(height + 4):  # generating border and padding for patterns
        grid.append([0 for x in range(width + 4)])
    return grid
            

# Compute the cell's next stage
def nextGen(y: int, x: int) -> int:
    alive = 0
    for i in range(4):
        index1 = i * 2
        index2 = index1 + 1
        rel_y, rel_x = y - pivot[0], x - pivot[1]
        b1 = int([rel_y + neighbors[index1][0], rel_x + neighbors[index1][1]] in livingCells)
        b2 = int([rel_y + neighbors[index2][0], rel_x + neighbors[index2][1]] in livingCells)
        alive += ((b1 & b2) << 1) | (b1 ^ b2)
    return int((alive == 3) or (world[y][x] and alive == 2))


# Apply nextGen() function to every cell within boundary and also update to its next state
def update():
    investigated = []
    for rel_y, rel_x in livingCells:
        y, x = rel_y + pivot[0], rel_x + pivot[1]
        if [y, x] not in investigated:
            investigated.append([y, x])
            world[y][x] = nextGen(y, x)

        for i, j in neighbors:
            y_neighbor, x_neighbor = y + i, x + j
            if [y_neighbor, x_neighbor] not in investigated:
                investigated.append([y_neighbor, x_neighbor])
                world[y_neighbor][x_neighbor] = nextGen(y_neighbor, x_neighbor)

    for y, x in investigated:
        rel_y, rel_x = y - pivot[0], x - pivot[1]
        if world[y][x] and ([rel_y, rel_x] not in livingCells):
            livingCells.append([rel_y, rel_x])
        elif (not world[y][x]) and ([rel_y, rel_x] in livingCells):
            livingCells.remove([rel_y, rel_x])


# Expand world if any padding contains a live cell
def addRowColumn():
    w = len(world[0])
    if 1 in world[1]:
        pivot[0] += 1
        world.insert(0, [0 for i in range(w)])

    if 1 in world[-2]:
        world.append([0 for i in range(w)])

    if 1 in [i[1] for i in world]:
        pivot[1] += 1
        for row in world:
            row.insert(0, 0)

    if 1 in [i[-2] for i in world]:
        for row in world:
            row.append(0)

        
# Display the world at each generation
def render():
    for y in range(1, len(world) - 1):
        for x in range(1, len(world[0]) - 1):
            if world[y][x]:
                print('⬜', end="")
            else:
                print('⬛', end="")
        print("\n", end="")


# ========================================================================= #
# ------------------------------ MAIN DRIVER ------------------------------ #
# ========================================================================= #

# Initialising variables/constants
worldWidth, worldHeight = 30, 30
neighbors = [[1, -1], [1, 0], 
             [1, 1], [0, 1], 
             [-1, 1], [-1, 0], 
             [-1, -1], [0, -1]]
livingCells = []
pivot = [0, 0] # (Δy, Δx)

# Loading pattern
default = input("(s)oup pattern or use one of the (d)efaults: ")
if default == 'd':
    from decoder import WIDTH, HEIGHT, pattern
    worldWidth, worldHeight = WIDTH, HEIGHT
    world = worldGen(worldWidth, worldHeight)
    pattern(world, livingCells)
else:
    world = worldGen(worldWidth, worldHeight)
    for y in range(2, len(world) - 2):
        for x in range(2, len(world[0]) - 2):
            state = random.randint(0,1)
            if state:
                world[y][x] = state
                livingCells.append([y, x])

# Displaying the pattern
render()
time.sleep(5)
os.system('cls')

# Start the evolution
while True:
    render()
    addRowColumn()
    update()
    time.sleep(0.1)
    os.system('cls')