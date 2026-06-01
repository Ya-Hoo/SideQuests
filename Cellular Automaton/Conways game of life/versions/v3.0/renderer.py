import pygame

# ========================================================================= #
# ------------------------------ RENDERER --------------------------------- #
# ========================================================================= #

# Colours
ALIVE_COL = (255, 255, 255)
DEAD_COL  = (20,  20,  20)
MENU_BG   = (30,  30,  30)
MENU_HL   = (70,  70, 120)
MENU_BORD = (80,  80,  80)
TEXT_COL  = (180, 180, 180)
HINT_COL  = (120, 120, 120)
GHOST_COL = (100, 100, 200, 160)

CELL_SIZE = 12   # pixels per cell
MENU_ROW_H = 22   # px per menu row
MENU_PADDING = 40   # px reserved for title + hint bar
SEARCH_H      = 22    # px height of the search input box


# Convert screen pixel coords to grid (row, col) cell coords.
def screen_to_cell(px: int, py: int, camera_x: int, camera_y: int) -> tuple[int, int]:
    col = px // CELL_SIZE + camera_x // CELL_SIZE
    row = py // CELL_SIZE + camera_y // CELL_SIZE
    return row, col


# Draw current generation & preview of new pattern
def render(screen: pygame.Surface, livingCells: set, camera_x: int, camera_y: int, ghost: list[tuple[int, int]] | None = None) -> None:
    screen.fill(DEAD_COL)
    W, H = screen.get_size()

    col_start = camera_x // CELL_SIZE - 1
    row_start = camera_y // CELL_SIZE - 1
    col_end = col_start + W // CELL_SIZE + 3
    row_end = row_start + H // CELL_SIZE + 3

    for (cy, cx) in livingCells:
        if col_start <= cx <= col_end and row_start <= cy <= row_end:
            px = (cx - camera_x // CELL_SIZE) * CELL_SIZE
            py = (cy - camera_y // CELL_SIZE) * CELL_SIZE
            pygame.draw.rect(screen, ALIVE_COL, (px, py, CELL_SIZE - 1, CELL_SIZE - 1))

    if ghost:
        ghost_surf = pygame.Surface((CELL_SIZE - 1, CELL_SIZE - 1), pygame.SRCALPHA)
        ghost_surf.fill(GHOST_COL)
        for (cy, cx) in ghost:
            if col_start <= cx <= col_end and row_start <= cy <= row_end:
                px = (cx - camera_x // CELL_SIZE) * CELL_SIZE
                py = (cy - camera_y // CELL_SIZE) * CELL_SIZE
                screen.blit(ghost_surf, (px, py))


# Status bar
def draw_hud(screen: pygame.Surface, font: pygame.font.Font, generation: int, fps: int, living: int, paused: bool, placing_pattern: bool) -> None:
    if placing_pattern:
        mode = "PLACE PATTERN — click to stamp  [Esc] cancel"
    elif paused:
        mode = "[SPACE] resume  [+/-] speed  [WASD] pan  [C] clear  [M] patterns  [R] random  [Q] quit"
    else:
        mode = "[SPACE] pause   [+/-] speed  [WASD] pan  [C] clear  [M] patterns  [R] random  [Q] quit"

    hud = font.render(f"Gen: {generation}   Alive: {living}   FPS: {fps}   {mode}", True, TEXT_COL)
    screen.blit(hud, (8, 8))


# Calculate number of menu rows
def _visible_rows(screen_h: int) -> int:
    panel_h = screen_h - 40
    return max(1, (panel_h - MENU_PADDING) // MENU_ROW_H)

# Draw pattern-selection side panel
def draw_menu(screen: pygame.Surface, font: pygame.font.Font, pattern_names: list[str], selected: int, scroll: int, query: str) -> None:
    W, H = screen.get_size()
    pw = 260
    vis = _visible_rows(H)
    ph = vis * MENU_ROW_H + MENU_PADDING
    panel_x = W - pw - 10
    panel_y = 30
 
    # Semi-transparent background
    panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
    panel.fill((*MENU_BG, 220))
    screen.blit(panel, (panel_x, panel_y))
    pygame.draw.rect(screen, MENU_BORD, (panel_x, panel_y, pw, ph), 1)
 
    # Title
    title = font.render("── Patterns ──", True, TEXT_COL)
    screen.blit(title, (panel_x + 10, panel_y + 6))
    
    # Search bar
    bar_x = panel_x + 6
    bar_y = panel_y + 24
    bar_w = pw - 12
    pygame.draw.rect(screen, MENU_BORD, (bar_x, bar_y, bar_w, SEARCH_H), 1)
    display_query = query if query else ""
    cursor = "|" if (pygame.time.get_ticks() // 500) % 2 == 0 else " "
    search_text = font.render(f"/{display_query}{cursor}", True,
                              ALIVE_COL if query else HINT_COL)
    screen.blit(search_text, (bar_x + 4, bar_y + 4))
 
    # Result count
    count_text = font.render(f"{len(pattern_names)} found", True, HINT_COL)
    screen.blit(count_text, (bar_x + bar_w - count_text.get_width() - 2, bar_y + 4))
 
    # Rows - only render the visible slice
    row_top = panel_y + 24 + SEARCH_H + 2
    for slot, i in enumerate(range(scroll, min(scroll + vis, len(pattern_names)))):
        iy = row_top + slot * MENU_ROW_H
        if i == selected:
            pygame.draw.rect(screen, MENU_HL, (panel_x + 4, iy - 1, pw - 8, MENU_ROW_H))
        label = font.render(pattern_names[i], True, ALIVE_COL if i == selected else TEXT_COL)
        screen.blit(label, (panel_x + 10, iy))
 
    # Hint bar
    hint = font.render("[↑↓] navigate  [Enter] place", True, HINT_COL)
    screen.blit(hint, (panel_x + 6, panel_y + ph - 16))