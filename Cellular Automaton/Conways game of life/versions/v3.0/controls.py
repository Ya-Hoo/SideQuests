import random
import pygame
from renderer import CELL_SIZE, screen_to_cell, _visible_rows

# ========================================================================= #
# -------------------------------- CONTROLS ------------------------------- #
# ========================================================================= #

PAN_SPEED = CELL_SIZE * 2

# How long to hold (ms) before continuous scroll starts, then interval between steps
SCROLL_DELAY  = 400
SCROLL_REPEAT = 10


# Keep menu_scroll so the selected item stays in the visible window.
def _clamp_scroll(state: dict) -> None:
    H = pygame.display.get_surface().get_height()
    vis = _visible_rows(H)
    n = len(state["pattern_names"])
    sel = state["menu_selected"]
    scroll = state["menu_scroll"]

    # Scroll down if selected is below visible window
    if sel >= scroll + vis:
        scroll = sel - vis + 1
    # Scroll up if selected is above visible window
    if sel < scroll:
        scroll = sel

    state["menu_scroll"] = max(0, min(scroll, max(0, n - vis)))


# Filter pattern_names from all_pattern_names by the current search query
def _apply_search(state: dict) -> None:
    query = state["search_query"].lower()
    if query:
        state["pattern_names"] = [
            n for n in state["all_pattern_names"] if query in n.lower()
        ]
    else:
        state["pattern_names"] = list(state["all_pattern_names"])
    state["menu_selected"] = 0
    state["menu_scroll"]   = 0


# Process all pygame events, including keyboard inputs
def handle_events(events: list, state: dict, livingCells: set) -> bool:
    for event in events:
        if event.type == pygame.QUIT:
            return False

        elif event.type == pygame.KEYDOWN:

            # Placing pattern
            if state["placing_pattern"]:
                if event.key == pygame.K_ESCAPE:
                    state["placing_pattern"] = False

            # Menu open
            elif state["menu_open"]:
                if event.key in (pygame.K_m, pygame.K_ESCAPE):
                    state["menu_open"] = False
 
                elif event.key == pygame.K_UP:
                    names = state["pattern_names"]
                    state["menu_selected"] = (state["menu_selected"] - 1) % len(names)
                    _clamp_scroll(state)
 
                elif event.key == pygame.K_DOWN:
                    names = state["pattern_names"]
                    state["menu_selected"] = (state["menu_selected"] + 1) % len(names)
                    _clamp_scroll(state)
 
                elif event.key == pygame.K_RETURN:
                    if state["pattern_names"]:
                        state["menu_open"] = False
                        state["placing_pattern"] = True
 
                elif event.key == pygame.K_BACKSPACE:
                    state["search_query"] = state["search_query"][:-1]
                    _apply_search(state)
 
                elif event.unicode and event.unicode.isprintable():
                    state["search_query"] += event.unicode
                    _apply_search(state)

            # Normal mode
            else:
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    return False
                elif event.key == pygame.K_SPACE:
                    state["paused"] = not state["paused"]
                elif event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                    state["fps"] = min(state["fps"] + 1, 60)
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    state["fps"] = max(state["fps"] - 1, 1)
                elif event.key == pygame.K_c:
                    livingCells.clear()
                    state["generation"] = 0
                elif event.key == pygame.K_r:
                    livingCells.update(
                        (y, x)
                        for y in range(1, 51)
                        for x in range(1, 51)
                        if random.randint(0, 1)
                    )
                elif event.key == pygame.K_m:
                    state["menu_open"] = True
                    state["placing_pattern"] = False
                    state["search_query"] = ""
                    state["pattern_names"] = list(state["all_pattern_names"])
                    state["menu_selected"] = 0
                    state["menu_scroll"] = 0

        # Mouse: cell toggling and pattern stamping
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if state["placing_pattern"]:
                livingCells.update(state["ghost_cells"])
                state["placing_pattern"] = False
            elif not state["menu_open"]:
                mx, my = event.pos
                cell = screen_to_cell(mx, my, state["camera_x"], state["camera_y"])
                if cell in livingCells:
                    livingCells.discard(cell)
                else:
                    livingCells.add(cell)

    return True


# Continuously scroll the menu while ↑/↓ is held, with an initial delay
def handle_menu_scroll(state: dict) -> None:
    if not state["menu_open"] or not state["pattern_names"]:
        return
 
    keys = pygame.key.get_pressed()
    now  = pygame.time.get_ticks()
    names = state["pattern_names"]
 
    direction = 0
    if keys[pygame.K_DOWN]:
        direction = 1
    elif keys[pygame.K_UP]:
        direction = -1
 
    if direction == 0:
        # No key held — reset tracker
        state["menu_scroll_dir"]       = 0
        state["menu_scroll_next_tick"] = 0
        return
 
    if direction != state.get("menu_scroll_dir", 0):
        # Key just changed direction — set initial delay
        state["menu_scroll_dir"]       = direction
        state["menu_scroll_next_tick"] = now + SCROLL_DELAY
        return
 
    if now >= state["menu_scroll_next_tick"]:
        state["menu_selected"] = (state["menu_selected"] + direction) % len(names)
        _clamp_scroll(state)
        state["menu_scroll_next_tick"] = now + SCROLL_REPEAT


# Handle world panning, unless menu is open then disable
def handle_pan(state: dict) -> None:
    if state["menu_open"]:
        return
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]  or keys[pygame.K_a]: state["camera_x"] -= PAN_SPEED
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]: state["camera_x"] += PAN_SPEED
    if keys[pygame.K_UP]    or keys[pygame.K_w]: state["camera_y"] -= PAN_SPEED
    if keys[pygame.K_DOWN]  or keys[pygame.K_s]: state["camera_y"] += PAN_SPEED


# Calculate where patterns will be stamped
def update_ghost(state: dict, patterns: dict) -> None:
    if not state["placing_pattern"]:
        state["ghost_cells"] = []
        return
    mx, my = pygame.mouse.get_pos()
    row, col = screen_to_cell(mx, my, state["camera_x"], state["camera_y"])
    name = state["pattern_names"][state["menu_selected"]]
    state["ghost_cells"] = [(row + dy, col + dx) for dy, dx in patterns[name]]