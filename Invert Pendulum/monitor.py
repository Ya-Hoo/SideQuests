import numpy as np
import matplotlib.pyplot as plt


class SimulationMonitor:
    def __init__(self):
        self.t = []

        self.x = []
        self.x_dot = []

        self.theta = []
        self.theta_dot = []

        self.u = []

    def record(self, time, state, force):
        x, x_dot, theta, theta_dot = state

        self.t.append(time)

        self.x.append(x)
        self.x_dot.append(x_dot)

        self.theta.append(abs(theta))
        self.theta_dot.append(theta_dot)

        self.u.append(force)

    def plot(self):
        t = np.array(self.t)
        
        # Create a figure with 5 rows and 1 column
        # figsize=(width, height) in inches
        fig, axs = plt.subplots(5, 1, figsize=(10, 15), sharex=True)
        fig.subplots_adjust(hspace=0.4) # Add space between plots

        # 1. Cart Position
        axs[0].plot(t, self.x, color='blue')
        axs[0].set_ylabel(r"$x$ (m)")
        axs[0].set_title("Cart Position")
        axs[0].grid(True, alpha=0.3)

        # 2. Cart Velocity
        axs[1].plot(t, self.x_dot, color='darkblue')
        axs[1].set_ylabel(r"$\dot x$ (m/s)")
        axs[1].set_title("Cart Velocity")
        axs[1].grid(True, alpha=0.3)

        # 3. Pendulum Angle
        axs[2].plot(t, self.theta, color='orange')
        axs[2].set_ylabel(r"$\theta$ (rad)")
        axs[2].set_title("Pendulum Angle")
        axs[2].grid(True, alpha=0.3)

        # 4. Angular Velocity
        axs[3].plot(t, self.theta_dot, color='darkorange')
        axs[3].set_ylabel(r"$\dot \theta$ (rad/s)")
        axs[3].set_title("Angular Velocity")
        axs[3].grid(True, alpha=0.3)

        # 5. Control Force
        axs[4].plot(t, self.u, color='red')
        axs[4].set_ylabel(r"$u$ (N)")
        axs[4].set_xlabel("Time (s)")
        axs[4].set_title("Control Force (u)")
        axs[4].grid(True, alpha=0.3)

        plt.show()