import pygame
import numpy as np
import random
from physics import InvertedPendulumPhysics
from renderer import PendulumRenderer, Button
from monitor import SimulationMonitor

# Configuration
S_CONFIG = 1  # 1 for Upright, -1 for Downward
TRACK_LIMIT = 0.5
M, m, L, g = 1, 0.05, 0.5, 9.81

def main():
    pygame.init()
    screen = pygame.display.set_mode((1250, 800))
    pygame.display.set_caption("Inverted Pendulum")
    
    # Initialize Physics and Renderer
    sim = InvertedPendulumPhysics(M, m, L, g)
    renderer = PendulumRenderer(1250, 800, 600)
    push_btn = Button(20, 60, 120, 40, "NUDGE")
    
    # Setup LQR
    K = sim.get_lqr_gain(s=S_CONFIG, Q_diag=[1, 50, 10, 20], R_val=1.0)
    
    # State: [x, x_dot, theta, theta_dot]
    if S_CONFIG == 1:
        state = np.array([0.5, 0.0, np.pi, 0.0])
        target = np.array([0, 0, 0, 0])
        mode_str = "UPRIGHT"
    else:
        state = np.array([0.5, 0.0, np.pi + 0.2, 0.0])
        target = np.array([0, 0, np.pi, 0])
        mode_str = "DOWNWARD"

    # Parameters to switch to LQR
    CATCH_ANGLE = 0.5
    
    # Set up monitoring
    monitor = SimulationMonitor()
    time = 0

    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 18)
    
    paused = True
    speed_multiplier = 0.75
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if push_btn.rect.collidepoint(event.pos):
                    push_btn.press()
                    nudge = random.uniform(-0.5, 0.5)
                    state[2] += nudge
                    state[3] = 0
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                if event.key == pygame.K_UP:
                    speed_multiplier = min(1.25, speed_multiplier + 0.25)
                if event.key == pygame.K_DOWN:
                    speed_multiplier = max(0.0, speed_multiplier - 0.25)

        u = 0.0
        if not paused:
            theta = state[2]
            theta = ((theta + np.pi) % (2 * np.pi)) - np.pi
            state[2] = theta
            
            # --- compute both controllers ---
            u_swing = sim.swing_up(state)

            x_vec = state - target
            u_lqr = -float((K @ x_vec).item())

            # --- blending factor based on angle ---
            alpha = min(1.0, abs(theta) / CATCH_ANGLE)

            # alpha = 1 → pure swing-up
            # alpha = 0 → pure LQR
            u = alpha * u_swing + (1 - alpha) * u_lqr

            # --- display mode ---
            if alpha < 0.5:
                mode_str = "STABILIZING (LQR)"
            else:
                mode_str = "SWING UP"
            
            # Physics Step
            dt = (1/60) * speed_multiplier
            state = sim.step(state, u, dt)
            
            time += dt
            monitor.record(time, state, u)
            
            # Hard Track Constraints
            if abs(state[0]) >= TRACK_LIMIT:
                state[0] = np.sign(state[0]) * TRACK_LIMIT
                state[1] = 0

        # Draw everything using the renderer
        renderer.draw_world(
            screen, state, u, TRACK_LIMIT, sim.L, 
            speed_multiplier, paused, mode_str, font, push_btn
        )
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    monitor.plot()

if __name__ == "__main__":
    main()