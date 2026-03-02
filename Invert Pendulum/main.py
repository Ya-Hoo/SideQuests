import pygame
import numpy as np
from physics import InvertedPendulumPhysics
from renderer import PendulumRenderer

# Configuration
S_CONFIG = 1  # 1 for Upright, -1 for Downward
TRACK_LIMIT = 0.5
M, m, L, g = 1, 0.05, 0.5, 9.81

def main():
    pygame.init()
    screen = pygame.display.set_mode((1250, 800))
    pygame.display.set_caption("Inverted Pendulum - Modular")
    
    # Initialize Physics and Renderer
    sim = InvertedPendulumPhysics(M, m, L, g)
    renderer = PendulumRenderer(1250, 800, 800)
    
    # Setup LQR
    K = sim.get_lqr_gain(s=S_CONFIG, Q_diag=[1, 100, 10, 100], R_val=0.05)
    
    # State: [x, x_dot, theta, theta_dot]
    if S_CONFIG == 1:
        state = np.array([0.3, 0.0, 0.2, 0.0])
        target = np.array([0, 0, 0, 0])
        mode_str = "UPRIGHT"
    else:
        state = np.array([0.3, 0.0, np.pi + 0.2, 0.0])
        target = np.array([0, 0, np.pi, 0])
        mode_str = "DOWNWARD"

    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 18)
    
    paused = True
    speed_multiplier = 0.75
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                if event.key == pygame.K_UP:
                    speed_multiplier = min(1.25, speed_multiplier + 0.25)
                if event.key == pygame.K_DOWN:
                    speed_multiplier = max(0.0, speed_multiplier - 0.25)

        u = 0.0
        if not paused:
            # Control: u = -K * (state - goal)
            x_vec = state - target
            u = -float((K @ x_vec).item())
            
            # Physics Step
            dt = (1/60) * speed_multiplier
            state = sim.step(state, u, dt)
            
            # Hard Track Constraints
            if abs(state[0]) >= TRACK_LIMIT:
                state[0] = np.sign(state[0]) * TRACK_LIMIT
                state[1] = 0

        # Draw everything using the renderer
        renderer.draw_world(
            screen, state, u, TRACK_LIMIT, sim.L, 
            speed_multiplier, paused, mode_str, font
        )
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()