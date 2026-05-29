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
        
        b1 = int((y + neighbors[index1][0], x + neighbors[index1][1]) in livingCells)
        b2 = int((y + neighbors[index2][0], x + neighbors[index2][1]) in livingCells)
        
        alive += ((b1 & b2) << 1) | (b1 ^ b2)
    return int((alive == 3) or (((y,x) in livingCells) and alive == 2))


# Apply nextGen() function to every cell within boundary and also update to its next state
def update():
    candidates = set()
    for y, x in livingCells:
        candidates.add((y,x))

        for i, j in neighbors:
            candidates.add((y+i, x+j))
            
    next_gen = {(y, x) for y, x in candidates if nextGen(y, x)}
    
    livingCells.clear()
    livingCells.update(next_gen)

        
# Display the world at each generation
def render():
    global lowY, highY, lowX, highX
    
    if not livingCells:
        print("(empty world)")
        return
 
    ys, xs = zip(*livingCells)
    minY, maxY = min(ys), max(ys)
    minX, maxX = min(xs), max(xs)
 
    lowY  = min(lowY,  minY)
    lowX  = min(lowX,  minX)
    highY = max(highY, maxY)
    highX = max(highX, maxX)
 
    rows = []
    for y in range(lowY, highY + 2):
        rows.append(''.join(
            '⬜' if (y, x) in livingCells else '⬛'
            for x in range(lowX, highX + 2)
        ))
    print('\n'.join(rows))


# ========================================================================= #
# ------------------------------ MAIN DRIVER ------------------------------ #
# ========================================================================= #

# Initialising variables/constants
neighbors = ((1, -1), (1, 0), 
             (1, 1), (0, 1), 
             (-1, 1), (-1, 0), 
             (-1, -1), (0, -1))
livingCells: set[tuple[int, int]] = set()
lowY, highY, lowX, highX = 0, 0, 0, 0

# Loading pattern
default = input("Use (d)efaults or press anything else to make random patterns: ")
if default == 'd':
    from decoder import pattern
    tmp = []
    pattern(tmp)
    livingCells = {tuple(c) for c in tmp}
else:
    livingCells = {
        (y, x)
        for y in range(1, 19)
        for x in range(1, 19)
        if random.randint(0, 1)
    }

# Displaying the pattern
render()
time.sleep(5)
os.system('cls' if os.name == 'nt' else 'clear')

# Start the evolution
while True:
    render()
    update()
    time.sleep(0.1)
    os.system('cls' if os.name == 'nt' else 'clear')