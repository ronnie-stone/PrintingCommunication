# -*- coding: utf-8 -*-
"""
Created on Thu Feb 20 00:29:56 2025

@author: Siddh
"""

import numpy as np
import matplotlib.pyplot as plt
from skopt import Optimizer
from skopt.learning.gaussian_process.kernels import RBF, WhiteKernel, ConstantKernel
from sklearn.gaussian_process import GaussianProcessRegressor
import random

# Bed dimensions
bedX = 320
bedY = 300

# Define the actual function (ground truth)
def bed_probe(x, y):
    return (0 - ((x**2 + y**2)**0.5) / 300)# + random.randrange(-100, 100)/3000)  # Simulated probe function

# Search space
smooth_space = [(0, bedX), (0, bedY)]

# Custom kernel for GP model
custom_kernel = ConstantKernel(1.0) * RBF(length_scale=30) + WhiteKernel(noise_level=1e-5)

# Create optimizer with GP model
smooth_optimizer = Optimizer(dimensions=smooth_space, base_estimator="GBRT", acq_func="LCB", initial_point_generator= "lhs")

# Collect data
data_X = []
data_Y = []

X_probed, Y_probed, Z_probed = [], [], []


# Initial data points
# init_points = [(0, 0), (0, 300), (280, 300), (280, 0), (140, 150)]
# for x, y in init_points:
#     z = bed_probe(x, y)
#     smooth_optimizer.tell([x, y], z)
#     data_X.append([x, y])
#     data_Y.append(z)
    

# Perform Bayesian optimization
for i in range(20):
    next_x, next_y = smooth_optimizer.ask()
    z_height = bed_probe(next_x, next_y)
    
    smooth_optimizer.tell([next_x, next_y], z_height)
    data_X.append([next_x, next_y])
    data_Y.append(z_height)
    
    X_probed.append(next_x)
    Y_probed.append(next_y)
    Z_probed.append(z_height)
    
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')
    scatter = ax.scatter(X_probed, Y_probed, Z_probed, c=Z_probed, cmap='viridis', s=50)

    ax.set_xlabel('X Position (mm)')
    ax.set_ylabel('Y Position (mm)')
    ax.set_zlabel('Z Offset (mm)')
    ax.set_title('Bayesian Optimization-Based Mesh Leveling')

    plt.colorbar(scatter, ax=ax, label='Z Offset (mm)')
    plt.show()
    
    
    

# Convert to numpy arrays
data_X = np.array(data_X)
data_Y = np.array(data_Y)

# **Manually Fit GP Model**
gp_model = GaussianProcessRegressor(kernel=custom_kernel, alpha=1e-3, n_restarts_optimizer=10)
gp_model.fit(data_X, data_Y)

# Create a mesh grid of X, Y values
x_range = np.linspace(0, bedX, 30)
y_range = np.linspace(0, bedY, 30)
X, Y = np.meshgrid(x_range, y_range)
grid_points = np.c_[X.ravel(), Y.ravel()]

# Compute actual function values
Z_actual = np.array([bed_probe(x, y) for x, y in grid_points]).reshape(X.shape)

# Predict function values using manually fitted GP
Z_pred, Z_std = gp_model.predict(grid_points, return_std=True)
Z_pred = Z_pred.reshape(X.shape)
Z_std = Z_std.reshape(X.shape)

# **Plot Actual Function**
fig1 = plt.figure(figsize=(10, 6))
ax1 = fig1.add_subplot(111, projection='3d')
ax1.plot_surface(X, Y, Z_actual, cmap='viridis', alpha=0.8)
ax1.set_xlabel("X Position (mm)")
ax1.set_ylabel("Y Position (mm)")
ax1.set_zlabel("Z Offset (mm)")
ax1.set_title("Actual Bed Function")

# **Plot Predicted Function**
fig2 = plt.figure(figsize=(10, 6))
ax2 = fig2.add_subplot(111, projection='3d')
ax2.plot_surface(X, Y, Z_pred, cmap='plasma', alpha=0.8)
ax2.set_xlabel("X Position (mm)")
ax2.set_ylabel("Y Position (mm)")
ax2.set_zlabel("Predicted Z Offset (mm)")
ax2.set_title("Predicted Function (Mean)")

# **Plot Uncertainty**
fig3 = plt.figure(figsize=(10, 6))
ax3 = fig3.add_subplot(111, projection='3d')
ax3.plot_surface(X, Y, Z_std, cmap='coolwarm', alpha=0.8)
ax3.set_xlabel("X Position (mm)")
ax3.set_ylabel("Y Position (mm)")
ax3.set_zlabel("Uncertainty (Std Dev)")
ax3.set_title("Uncertainty Surface of Bayesian Optimization")

Z_error = abs(Z_actual-Z_pred)

fig4 = plt.figure(figsize=(10, 6))
ax4 = fig4.add_subplot(111, projection='3d')
ax4.plot_surface(X,Y,Z_error, cmap='coolwarm', alpha=0.8)
ax4.set_xlabel("X Position (mm)")
ax4.set_ylabel("Y Position (mm)")
ax4.set_zlabel("Error")
ax4.set_title("Error surface of Bayesian Optimization")

plt.show()
