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

        self.theta.append(theta)
        self.theta_dot.append(theta_dot)

        self.u.append(force)

    def plot(self):

        t = np.array(self.t)

        plt.figure()
        plt.plot(t, self.x)
        plt.xlabel("Time (s)")
        plt.ylabel("Cart Position (m)")
        plt.title("Cart Position vs Time")

        plt.figure()
        plt.plot(t, self.x_dot)
        plt.xlabel("Time (s)")
        plt.ylabel("Cart Velocity (m/s)")
        plt.title("Cart Velocity vs Time")

        plt.figure()
        plt.plot(t, self.theta)
        plt.xlabel("Time (s)")
        plt.ylabel("Pendulum Angle (rad)")
        plt.title("Pendulum Angle vs Time")

        plt.figure()
        plt.plot(t, self.theta_dot)
        plt.xlabel("Time (s)")
        plt.ylabel("Angular Velocity (rad/s)")
        plt.title("Pendulum Angular Velocity vs Time")

        plt.figure()
        plt.plot(t, self.u)
        plt.xlabel("Time (s)")
        plt.ylabel("Force (N)")
        plt.title("Control Force vs Time")

        plt.show()