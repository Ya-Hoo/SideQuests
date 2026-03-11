import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import solve_continuous_are

class InvertedPendulumPhysics:
    def __init__(self, M=1.0, m=0.05, L=0.5, g=9.81):
        self.M = M
        self.m = m
        self.L = L
        self.g = g
        
    def get_lqr_gain(self, s, Q_diag, R_val):
        """Computes LQR gain matrix K."""
        # A and B matrices
        A = np.array([
            [0, 1, 0, 0],
            [0, 0, self.m*self.g/self.M, 0],
            [0, 0, 0, 1],
            [0, 0, s*(self.M+self.m)*self.g/(self.M*self.L), 0]
        ])
        B = np.array([[0], [1/self.M], [0], [s/(self.M*self.L)]])
        R = np.array([[R_val]])
        Q = np.diag(Q_diag)

        P = solve_continuous_are(A, B, Q, R)
        return np.linalg.inv(R) @ B.T @ P

    def dynamics(self, t, y, u):
        _, x_dot, theta, theta_dot = y
        S, C = np.sin(theta), np.cos(theta)
        denom = self.M + self.m * S**2

        x_ddot = (u + self.m * S * (-self.L * theta_dot**2 + self.g * C)) / denom
        theta_ddot = (u * C - self.m * self.L * theta_dot**2 * S * C + (self.M + self.m) * self.g * S) / (self.L * denom)
        
        return [x_dot, x_ddot, theta_dot, theta_ddot]

    def step(self, state, u, dt):
        sol = solve_ivp(self.dynamics, [0, dt], state, args=(u,), t_eval=[dt])
        return sol.y[:, -1]
    
    def swing_up(self, state, k_push=3.5, k_center=1.2):
        x, x_dot, theta, theta_dot = state

        # Swing pumping
        u_swing = k_push * np.tanh(1.5 * theta_dot * np.cos(theta))

        # Centering
        u_center = -k_center * x - 0.5 * x_dot

        # Reduce force near track edges
        track_limit = 1.0
        scale = max(0.0, 1 - abs(x) / track_limit)

        return scale * u_swing + u_center