# conda install -c conda-forge bayesian-optimization
import numpy as np
from skopt import Optimizer
from skopt import plots
import matplotlib.pyplot as plt
import random

bedX = 320
bedY = 300

smooth_space = [(0,bedX-20), (0,bedY)]
rough_space = [(bedX-20, bedX), (0, bedY)]
def bed_probe(x,y):
    
    # base_request = ("http://{0}:{1}/rr_gcode?gcode=" + "G30" + filename).format(self.IP,"")
    return (0 - ((x**2+y**2)**0.5)/3000)# + random.randrange(-100, 100)/3000)

smooth_optimizer = Optimizer(dimensions=smooth_space, base_estimator="rf")
noisy_optimizer = Optimizer(dimensions=rough_space, base_estimator="rf")

# {(x, y): z}
data = {}



smooth_optimizer.tell([0, 0], bed_probe(0, 0))
smooth_optimizer.tell([0, 300], bed_probe(0, 300))
smooth_optimizer.tell([280, 300], bed_probe(300, 300))
smooth_optimizer.tell([280, 0], bed_probe(300, 0))
smooth_optimizer.tell([140, 150], bed_probe(0, 0))



for i in range(50):
    # Suggest next probing point'
    if i == 0 :
        print("first run")
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


plots.plot_evaluations(smooth_optimizer.get_result())
plots.plot_objective(smooth_optimizer.get_result())