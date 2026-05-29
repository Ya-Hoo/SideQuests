import re
import os

# ── File loading ──────────────────────────────────────────────────────────
FILENAME = input("Enter file name: ")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, '..', '..', 'all', FILENAME), 'r') as f:
    lines = [line.strip() for line in f if not line.startswith('#')]

# ── Header parsing ────────────────────────────────────────────────────────
# Handles any combination of fields: x, y, rule (rule is optional)
header = {k.strip(): v.strip() for k, _, v in
          (field.partition('=') for field in lines[0].split(','))}

WIDTH  = int(header['x'])
HEIGHT = int(header['y'])
RULE   = header.get('rule', 'B3/S23')

# ── RLE body tokenisation ─────────────────────────────────────────────────
# Join all lines after the header; strip the terminal '!'
raw_body = ''.join(lines[1:]).rstrip('!')

_TOKEN = re.compile(r'(\d*)([bo$])')

PATTERN_RAW: list[list[tuple[int, str]]] = []
current_row: list[tuple[int, str]] = []

for count_str, cell in _TOKEN.findall(raw_body):
    count = int(count_str) if count_str else 1
    if cell == '$':
        PATTERN_RAW.append(current_row)
        current_row = []
        # count > 1 means that many row endings (i.e. count-1 blank rows follow)
        for _ in range(count - 1):
            PATTERN_RAW.append([])
    else:
        current_row.append((count, cell))

if current_row:          # last row if file omits the final '$'
    PATTERN_RAW.append(current_row)

# ── Public API ────────────────────────────────────────────────────────────
def pattern(alive: list) -> None:
    """Populate alive with [y, x] coords of every live cell."""
    for y, row in enumerate(PATTERN_RAW, start=1):
        x = 1
        for count, cell in row:
            if cell == 'o':
                alive.extend([y, x + j] for j in range(count))
            x += count          # advance past both 'o' and 'b' runs