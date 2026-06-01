import os
import re
import pygame

from logic import update
from renderer import CELL_SIZE, render, draw_hud, draw_menu
from controls import handle_events, handle_pan, handle_menu_scroll, update_ghost

# ========================================================================= #
# --------------------------- PATTERN LOADING ----------------------------- #
# ========================================================================= #

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
ALL_DIR   = os.path.join(BASE_DIR, '..', '..', 'all')

_TOKEN = re.compile(r'(\d*)([bo$])')

# Parse an RLE file and return a list of (dy, dx) live-cell offsets.
def load_rle(filepath: str) -> list[tuple[int, int]]:
    with open(filepath, 'r') as f:
        lines = [l.strip() for l in f if not l.startswith('#')]

    body = ''.join(lines[1:]).rstrip('!')
    rows: list[list] = []
    current: list    = []
 
    for count_str, cell in _TOKEN.findall(body):
        count = int(count_str) if count_str else 1
        if cell == '$':
            rows.append(current)
            current = []
            for _ in range(count - 1):
                rows.append([])
        else:
            current.append((count, cell))
    if current:
        rows.append(current)
 
    cells: list[tuple[int, int]] = []
    for y, row in enumerate(rows):
        x = 0
        for count, cell in row:
            if cell == 'o':
                for j in range(count):
                    cells.append((y, x + j))
            x += count
    return cells


# Scan the all/ folder and return file name for every RLE.
def scan_patterns() -> dict[str, list[tuple[int, int]]]:
    patterns: dict[str, list[tuple[int, int]]] = {}
    if not os.path.isdir(ALL_DIR):
        print(f"[warn] Pattern folder not found: {ALL_DIR}")
        return patterns
    for fname in sorted(os.listdir(ALL_DIR)):
        if fname.lower().endswith('.rle'):
            name = os.path.splitext(fname)[0].replace('_', ' ').replace('-', ' ')
            try:
                patterns[name] = load_rle(os.path.join(ALL_DIR, fname))
            except Exception as e:
                print(f"[warn] Could not load {fname}: {e}")
    return patterns


# ========================================================================= #
# ------------------------------ MAIN DRIVER ------------------------------ #
# ========================================================================= #

livingCells: set[tuple[int, int]] = set()

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((1000, 800), pygame.RESIZABLE)
pygame.display.set_caption("Conway's Game of Life")
clock = pygame.time.Clock()
font = pygame.font.SysFont("monospace", 14)

W, H = screen.get_size()

# Patterns
patterns = scan_patterns()
pattern_names = list(patterns.keys())

# Shared state dict
state: dict = {
    "camera_x":              0,
    "camera_y":              0,
    "fps":                   10,
    "paused":                True,
    "generation":            0,
    "menu_open":             False,
    "menu_selected":         0,
    "menu_scroll":           0,
    "menu_scroll_dir":       0,
    "menu_scroll_next_tick": 0,
    "placing_pattern":       False,
    "ghost_cells":           [],
    "all_pattern_names":     pattern_names,
    "pattern_names":         list(pattern_names),
    "search_query":          "",
}

# Main loop 
running = True
while running:
    update_ghost(state, patterns)
    running = handle_events(pygame.event.get(), state, livingCells)
    handle_pan(state)
    handle_menu_scroll(state)
 
    render(screen, livingCells, state["camera_x"], state["camera_y"], state["ghost_cells"])
    draw_hud(screen, font, state["generation"], state["fps"],
             len(livingCells), state["paused"], state["placing_pattern"])
 
    if state["menu_open"]:
        draw_menu(screen, font, state["pattern_names"],
                  state["menu_selected"], state["menu_scroll"],
                  state["search_query"])
 
    if not state["paused"] and not state["placing_pattern"]:
        update(livingCells)
        state["generation"] += 1
 
    pygame.display.flip()
    clock.tick(state["fps"])
 
pygame.quit()