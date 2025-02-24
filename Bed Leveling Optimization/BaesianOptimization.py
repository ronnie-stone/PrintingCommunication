# conda install -c conda-forge bayesian-optimization
import numpy as np
from skopt import Optimizer
from skopt import plots
from skopt.learning.gaussian_process.kernels import RBF, WhiteKernel, ConstantKernel

import matplotlib.pyplot as plt
import random

bedX = 320
bedY = 300

smooth_space = [(0,bedX-20), (0,bedY)]
rough_space = [(bedX-20, bedX), (0, bedY)]
def bed_probe(x,y):
    
    # base_request = ("http://{0}:{1}/rr_gcode?gcode=" + "G30" + filename).format(self.IP,"")
    return (0 - ((x**2+y**2)**0.5)/3000 + random.randrange(-100, 100)/3000)


smooth_optimizer = Optimizer(dimensions=smooth_space, base_estimator="gp", acq_func = "LCB", acq_func_kwargs={"xi": 0.01}
)

custom_kernel = ConstantKernel(1.0) * RBF(length_scale=50) + WhiteKernel(noise_level=1e-6)
smooth_optimizer.base_estimator_.kernel = custom_kernel


noisy_optimizer = Optimizer(dimensions=rough_space, base_estimator="rf")

# {(x, y): z}
data = {}



smooth_optimizer.tell([0, 0], bed_probe(0, 0))
smooth_optimizer.tell([0, 300], bed_probe(0, 300))
smooth_optimizer.tell([280, 300], bed_probe(300, 300))
smooth_optimizer.tell([280, 0], bed_probe(300, 0))
smooth_optimizer.tell([140, 150], bed_probe(0, 0))



x_range = np.linspace(0, bedX - 20, 30)  # Adjust resolution if needed
y_range = np.linspace(0, bedY, 30)
X, Y = np.meshgrid(x_range, y_range)
grid_points = np.c_[X.ravel(), Y.ravel()]  # Convert to (N, 2) array for prediction




for i in range(20):
    # Suggest next probing point'
    if i == 0 :
        print("first run")
    next_x, next_y = smooth_optimizer.ask()
    
    while (next_x, next_y) in data.keys():
        next_x, next_y = smooth_optimizer.ask()
        
    # Probe the bed at the suggested point
    z_height = bed_probe(next_x, next_y)
    
    data[(next_x, next_y)] = z_height

    # Update optimizer with new data
    smooth_optimizer.tell([next_x, next_y], z_height)
    
    # Convert to numpy arrays
    X_probed = np.array([key[0] for key in data.keys()])
    Y_probed = np.array([key[1] for key in data.keys()])
    Z_probed = np.array([data[key] for key in data.keys()])

    # Plot the bed level mesh
    fig = plt.figure(figsize=(8,6))
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(X_probed, Y_probed, Z_probed, c=Z_probed, cmap='viridis')
    ax.set_xlabel('X Position (mm)')
    ax.set_ylabel('Y Position (mm)')
    ax.set_zlabel('Z Offset (mm)')
    ax.set_title('Bayesian Optimization-Based Mesh Leveling')
    plt.show()
    
    
    # **Predict function values and uncertainty**
    # gp_model = smooth_optimizer.base_estimator_  # Extract Gaussian Process model
    # Z_pred, Z_std = gp_model.predict(grid_points, return_std=True)

    # # Reshape for plotting
    # Z_std = Z_std.reshape(X.shape)

    # # **Plot 3D Uncertainty Surface**
    # fig = plt.figure(figsize=(10, 6))
    # ax = fig.add_subplot(111, projection='3d')
    # ax.plot_surface(X, Y, Z_std, cmap='coolwarm', alpha=0.8)
    # ax.set_xlabel("X Position (mm)")
    # ax.set_ylabel("Y Position (mm)")
    # ax.set_zlabel("Uncertainty (Std Dev)")
    # ax.set_title("Uncertainty Surface of the Bayesian Optimization")

    # plt.show()



plots.plot_evaluations(smooth_optimizer.get_result())
plots.plot_objective(smooth_optimizer.get_result())


# Create a mesh grid of X, Y values
x_range = np.linspace(0, bedX - 20, 30)  
y_range = np.linspace(0, bedY, 30)
X, Y = np.meshgrid(x_range, y_range)
grid_points = np.c_[X.ravel(), Y.ravel()]  

# Compute actual function values
Z_actual = np.array([bed_probe(x, y) for x, y in grid_points]).reshape(X.shape)

# Predict function values using GP model
gp_model = smooth_optimizer.base_estimator_
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

plt.show()