import os
import time

import patterns


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


def worldGen(width:int, height:int) -> list:
    grid = []
    global pivot
    pivot = [0, 0]
    for y in range(0, height + 2):  # generating border to handle edge/corner cases
        line = []
        for x in range(0, width + 2):
            line.append(Cell(y, x))
        grid.append(line)
    return grid
            

def nextGen():  # compute the cell's next stage
    for y in range(1, len(world) - 1):
        for x in range(1, len(world[0]) - 1):
            world[y][x].nextGen()


def update():  # update cell's state after every computation is done
    for y in range(1, len(world) - 1):
        for x in range(1, len(world[0]) - 1):
            world[y][x].currState = world[y][x].nextState


def addRowColumn():  # expand world if cell requires new space
    top = world[1]
    bottom = world[-2]
    left = [i[1] for i in world[1:-1]]
    right = [i[-2] for i in world[1:-1]]
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

def render():
    for y in range(1, len(world) - 1):
        for x in range(1, len(world[0]) - 1):
            if world[y][x].currState == 0:
                print('⬛', end="")
            else:
                print('⬜', end="")
        print("\n", end="")


# Main driver
if __name__ == "__main__":
    worldWidth, worldHeight = 10, 10
    world = worldGen(worldWidth, worldHeight)
    pivot = (0, 0) # (Δy, Δx)

    patterns.LWSS(world)  # place something in the world
    
    while True:
        render()
        addRowColumn()
        nextGen()
        update()
        time.sleep(0.1)
        os.system('cls')
