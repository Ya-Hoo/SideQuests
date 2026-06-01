# ========================================================================= #
# --------------------------------- LOGIC --------------------------------- #
# ========================================================================= #

NEIGHBORS = ((1, -1), (1, 0),
             (1,  1), (0, 1),
             (-1, 1), (-1, 0),
             (-1,-1), (0, -1))


def nextGen(y: int, x: int, livingCells: set) -> int:
    """Compute the cell's next state using bit-manipulation logic."""
    alive = 0
    for i in range(4):
        index1 = i * 2
        index2 = index1 + 1
        b1 = int((y + NEIGHBORS[index1][0], x + NEIGHBORS[index1][1]) in livingCells)
        b2 = int((y + NEIGHBORS[index2][0], x + NEIGHBORS[index2][1]) in livingCells)
        alive += ((b1 & b2) << 1) | (b1 ^ b2)
    return int((alive == 3) or ((y, x) in livingCells and alive == 2))


def update(livingCells: set) -> None:
    """Advance the world by one generation in-place."""
    candidates: set[tuple[int, int]] = set()
    for cy, cx in livingCells:
        candidates.add((cy, cx))
        for dy, dx in NEIGHBORS:
            candidates.add((cy + dy, cx + dx))

    next_gen = {(cy, cx) for cy, cx in candidates if nextGen(cy, cx, livingCells)}
    livingCells.clear()
    livingCells.update(next_gen)