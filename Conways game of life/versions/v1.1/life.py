import os, time, random


class Cell:
    def __init__(self, y, x):
        self.currState = 0
        self.nextState = 0
        self.y = y - pivot[0]
        self.x = x - pivot[1]

        self.adjacent = [[self.y + 1, self.x], [self.y - 1, self.x], [self.y, self.x + 1], [self.y, self.x - 1], 
                [self.y + 1, self.x + 1], [self.y + 1, self.x - 1], [self.y - 1, self.x + 1], [self.y - 1, self.x - 1]]

    def nextGen(self):
        population = 0
        for coord in self.adjacent:
            if world[coord[0] + pivot[0]][coord[1] + pivot[1]].currState:
                population += 1
        if self.currState == 1:  # Game of Life rules
            if population == 2 or population == 3:
                self.nextState = 1
            else:
                self.nextState = 0
        else:
            if population == 3:
                self.nextState = 1


# Create empty world as a 2D array
def worldGen(width:int, height:int) -> list:
    grid = []
    for y in range(0, height + 4):  # generating border and padding for patterns
        line = []
        for x in range(0, width + 4):
            line.append(Cell(y, x))
        grid.append(line)
    return grid
            

# Compute the cell's next stage
def nextGen() -> None:
    for y in range(1, len(world) - 1):
        for x in range(1, len(world[0]) - 1):
            world[y][x].nextGen()


# Update cell's state after every computation is done
def update() -> None:
    for y in range(1, len(world) - 1):
        for x in range(1, len(world[0]) - 1):
            world[y][x].currState = world[y][x].nextState


# Expand world if any padding is filled up
def addRowColumn() -> None:  
    top = world[1]
    bottom = world[-2]
    left = [i[1] for i in world]
    right = [i[-2] for i in world]
    w = len(world[0])
    h = len(world)
    for organism in top:
        if organism.currState == 1:
            pivot[0] += 1
            world.insert(0, [Cell(0, x) for x in range(w)])
            break

    for organism in bottom:
        if organism.currState == 1:
            world.append([Cell(h, x) for x in range(w)])
            break

    for organism in left:
        if organism.currState == 1:
            pivot[1] += 1
            for y, row in enumerate(world, 0):
                row.insert(0, Cell(y, 0))
            break

    for organism in right:
        if organism.currState == 1:
            for y, row in enumerate(world, 0):
                row.append(Cell(y, w))
            break


# Display the world and its evolvement
def render() -> None:
    for y in range(1, len(world) - 1):
        for x in range(1, len(world[0]) - 1):
            if world[y][x].currState == 0:
                print('⬛', end="")
            else:
                print('⬜', end="")
        print("\n", end="")


# Main driver
worldWidth, worldHeight = 30, 30
pivot = [0, 0] # (Δy, Δx)

default = input("(r)andom pattern or use one of the (d)efaults: ")
if default == 'd':
    from decoder import *
    worldWidth, worldHeight = WIDTH, HEIGHT
    world = worldGen(worldWidth, worldHeight)
    pattern(world) # Place pattern into world
else:
    world = worldGen(worldWidth, worldHeight)
    for y in range(2, len(world) - 2):
        for x in range(2, len(world[0]) - 2):
            world[y][x].currState = random.randint(0,1)

render()
time.sleep(5)
os.system('cls')

while True:
    render()
    addRowColumn()
    nextGen()
    update()
    time.sleep(0.1)
    os.system('cls')