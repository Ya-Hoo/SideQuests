import pygame
import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import solve_continuous_are

# ==============================
# Physical Parameters (SI units)
# ==============================
M = 1     # mass of cart
m = 0.05     # mass of pendulum bob
L = 0.5     # length of rod
g = 9.81    # gravity

TRACK_LENGTH = 1.5
TRACK_LIMIT = TRACK_LENGTH / 2
FORCE_LIMIT = 30.0

s = 1   # s=1 is pendulum up (theta=0)

# ==============================
# Linearized Matrices
# ==============================
def linearized_matrices(M, m, L, g, s):

    A = np.array([
        [0, 1, 0, 0],
        [0, 0, m*g/M, 0],
        [0, 0, 0, 1],
        [0, 0, s*(M+m)*g/(M*L), 0]
    ])

    B = np.array([
        [0],
        [1/M],
        [0],
        [s/(M*L)]
    ])

    return A, B


A, B = linearized_matrices(M, m, L, g, s)

Q = np.diag([
    1,     # cart position (small penalty)
    1,      # cart velocity
    10,   # angle (very important)
    100     # angular velocity
])

R = np.array([[0.05]])  # penalize force

# Solve Riccati equation
P = solve_continuous_are(A, B, Q, R)

# Compute gain
K = np.linalg.inv(R) @ B.T @ P

# ==============================
# Nonlinear Dynamics
# ==============================
def dynamics(t, y, u):
    x, x_dot, theta, theta_dot = y

    S = np.sin(theta)
    C = np.cos(theta)
    denom = M + m * S**2

    x_ddot = (u + m*S*(-L*theta_dot**2 + g*C)) / denom

    theta_ddot = (u*C - m*L*theta_dot**2*C*S + (M+m)*g*S) / (L*denom)

    return [x_dot, x_ddot, theta_dot, theta_ddot]


# ==============================
# Simulation Settings
# ==============================
base_dt = 1/60
speed_multiplier = 0.75
paused = True

# Initial condition (slightly perturbed upright)
if s == 1:
    state = np.array([0.3, 0.0, 0.2, 0.0])
else:
    state = np.array([0.3, 0.0, np.pi + 0.2, 0.0])


# ==============================
# Pygame Setup
# ==============================
def draw_ruler(screen, center_x, cart_y, scale, track_limit, font):

    major_step = 0.1
    minor_step = 0.05

    left_limit = -track_limit
    right_limit = track_limit

    # Create transparent overlay surface
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

    # ---------- Minor ticks (very subtle) ----------
    x_val = left_limit
    while x_val <= right_limit:
        px = center_x + int(x_val * scale)

        pygame.draw.line(
            overlay,
            (120, 120, 140, 40),   # RGBA (low alpha)
            (px, cart_y - 20),
            (px, cart_y + 20),
            1
        )

        x_val += minor_step

    # ---------- Major ticks + small labels ----------
    x_val = left_limit
    while x_val <= right_limit + 1e-6:
        px = center_x + int(x_val * scale)

        pygame.draw.line(
            overlay,
            (160, 160, 180, 90),   # Slightly stronger alpha
            (px, cart_y - 30),
            (px, cart_y + 30),
            2
        )

        label = font.render(f"{x_val:.2f}", True, (150, 150, 170))
        overlay.blit(label, (px - 16, cart_y + 55))

        x_val += major_step

    # Blit overlay
    screen.blit(overlay, (0, 0))


pygame.init()
width, height = 1250, 800
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Inverted Pendulum")
clock = pygame.time.Clock()

scale = 800
CART_LENGTH_M = 0.067     # 50 mm
CART_HEIGHT_M = 0.05     # 30 mm visual thickness

cart_width = int(CART_LENGTH_M * scale)
cart_height = int(CART_HEIGHT_M * scale)

BG = (15, 15, 20)
TRACK = (70, 70, 80)
LIMIT = (0, 180, 200)
CART = (230, 230, 235)
ROD = (255, 170, 60)
MASS = (100, 180, 255)
TEXT = (180, 180, 190)

font = pygame.font.SysFont("consolas", 18)

# ==============================
# Main Loop
# ==============================
running = True
while running:
    clock.tick(60)

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

    if not paused:

        dt = base_dt * speed_multiplier
        x, x_dot, theta, theta_dot = state

        x_eq = np.array([0, 0, 0 if s == 1 else np.pi, 0])
        x_vec = state - x_eq

        # State feedback
        u = -float((K @ x_vec).item())

        # Integrate nonlinear dynamics
        sol = solve_ivp(
            dynamics,
            [0, dt],
            state,
            args=(u,),
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
        u = 0

    # ==============================
    # Drawing
    # ==============================
    screen.fill(BG)
    offset = -200
    cart_y = height // 2 - offset
    cart_x = width // 2 + int(x * scale)
    draw_ruler(screen, width//2, cart_y, scale, TRACK_LIMIT, font)

    left_limit = width//2 - int(TRACK_LIMIT * scale)
    right_limit = width//2 + int(TRACK_LIMIT * scale)

    pygame.draw.line(screen, TRACK,
                     (left_limit, cart_y),
                     (right_limit, cart_y), 4)

    pygame.draw.line(screen, LIMIT,
                     (left_limit, cart_y+40),
                     (left_limit, cart_y-40), 3)
    pygame.draw.line(screen, LIMIT,
                     (right_limit, cart_y+40),
                     (right_limit, cart_y-40), 3)

    cart_rect = pygame.Rect(
        cart_x - cart_width//2,
        cart_y - cart_height//2,
        cart_width,
        cart_height
    )
    pygame.draw.rect(screen, CART, cart_rect, border_radius=6)

    pend_x = cart_x - int(L * scale * np.sin(theta))
    pend_y = cart_y - int(L * scale * np.cos(theta)) - offset

    pygame.draw.line(screen, ROD,
                     (cart_x, cart_y),
                     (pend_x, pend_y), 6)

    pygame.draw.circle(screen, MASS, (pend_x, pend_y), 10)

    status = "PAUSED" if paused else "RUNNING"
    mode = "UPRIGHT" if s == +1 else "DOWNWARD"

    info = (
        f"{mode} | "
        f"x={x: .3f}  "
        f"theta={theta: .3f}  "
        f"u={u: .2f}N  "
        f"speed={speed_multiplier:.2f}x  "
        f"{status}"
    )

    text_surface = font.render(info, True, TEXT)
    screen.blit(text_surface, (20, 20))

    pygame.display.flip()

pygame.quit()