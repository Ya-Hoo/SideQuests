import pygame
import numpy as np
from scipy.integrate import solve_ivp


# ------------------
# PHYSICAL CONSTANTS
# ------------------
M = 1.0     # mass of cart (kg)
m = 0.2     # mass of pendulum bob (kg)
L = 0.5     # length of pendulum (m)
g = 9.81    # gravity (m/s2)

# initial state of pendulum
# state = [x, x_dot, theta, theta_dot]
state = np.array([0.0, 0.0, 0.2, 0.0])

TRACK_LENGTH = 1.0
TRACK_LIMIT = TRACK_LENGTH / 2

base_dt = 1/60      # 60 fps


# ------------------
# SIMULATION SETTINGS
# ------------------
FORCE_MAG = 5.0
speed_multiplier = 0.5   # default 0.5x speed
paused = True            # start paused


# ------------------
# Dynamics
# ------------------
def dynamics(t, y, u):
    x, x_dot, theta, theta_dot = y
    
    S = np.sin(theta)
    C = np.cos(theta)
    denominator = M + m * S**2

    # Equations of motion
    x_ddot = (u + m*S*(-L*theta_dot**2 + g*C)) / denominator
    theta_ddot = (u*C - m*L*theta_dot**2*C*S + (M+m)*g*S) / (L*denominator)

    return [x_dot, x_ddot, theta_dot, theta_ddot]

# ------------------
# Pygame Setup
# ------------------
pygame.init()
width, height = 1000, 650
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Inverted Pendulum")
clock = pygame.time.Clock()

scale = 400
cart_width = 90
cart_height = 45

# Colors
BG = (18, 18, 22)
TRACK = (80, 80, 90)
LIMIT = (0, 180, 200)
CART = (230, 230, 235)
ROD = (255, 170, 60)
MASS = (100, 180, 255)
TEXT = (180, 180, 190)

font = pygame.font.SysFont("consolas", 18)

running = True
while running:
    clock.tick(60)

    # ------------------
    # Input
    # ------------------
    u = 0
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        u = -FORCE_MAG
    if keys[pygame.K_RIGHT]:
        u = FORCE_MAG

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused
            if event.key == pygame.K_UP:
                speed_multiplier += .25
            if event.key == pygame.K_DOWN:
                speed_multiplier -= .25

    # ------------------
    # Physics Integration
    # ------------------
    if not paused:
        dt = base_dt * speed_multiplier

        sol = solve_ivp(
            dynamics,
            [0, dt],
            state,
            args=(u,),
            method='RK45',
            t_eval=[dt]
        )

        state = sol.y[:, -1]
        x, x_dot, theta, theta_dot = state

        # Track constraint
        if x <= -TRACK_LIMIT:
            x = -TRACK_LIMIT
            x_dot = 0
        if x >= TRACK_LIMIT:
            x = TRACK_LIMIT
            x_dot = 0

        state = np.array([x, x_dot, theta, theta_dot])
    else:
        x, x_dot, theta, theta_dot = state

    # ------------------
    # Drawing
    # ------------------
    screen.fill(BG)

    cart_y = height // 2
    cart_x = width // 2 + int(x * scale)

    left_limit = width//2 - int(TRACK_LIMIT * scale)
    right_limit = width//2 + int(TRACK_LIMIT * scale)

    # Track
    pygame.draw.line(screen, TRACK,
                     (left_limit, cart_y),
                     (right_limit, cart_y), 4)

    # Limits
    pygame.draw.line(screen, LIMIT,
                     (left_limit, cart_y+60),
                     (left_limit, cart_y-60), 3)
    pygame.draw.line(screen, LIMIT,
                     (right_limit, cart_y+60),
                     (right_limit, cart_y-60), 3)

    # Cart
    cart_rect = pygame.Rect(
        cart_x - cart_width//2,
        cart_y - cart_height//2,
        cart_width,
        cart_height
    )
    pygame.draw.rect(screen, CART, cart_rect, border_radius=10)

    # Pendulum
    pend_x = cart_x + int(L * scale * np.sin(theta))
    pend_y = cart_y - int(L * scale * np.cos(theta))

    pygame.draw.line(screen, ROD,
                     (cart_x, cart_y),
                     (pend_x, pend_y), 6)

    pygame.draw.circle(screen, MASS, (pend_x, pend_y), 10)

    # HUD
    status = "PAUSED" if paused else "RUNNING"
    info = (
        f"x = {x: .3f} m   "
        f"theta = {theta: .3f} rad   "
        f"u = {u: .1f} N   "
        f"speed = {speed_multiplier: .2f}x   "
        f"{status}"
    )

    text_surface = font.render(info, True, TEXT)
    screen.blit(text_surface, (20, 20))

    pygame.display.flip()

pygame.quit()