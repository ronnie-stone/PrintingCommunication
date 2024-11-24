import time
import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from shapely.geometry import Polygon, LineString
from shapely.affinity import rotate, translate


def transform_to_global(local_origin, robot_base, theta_local, end_effector_local, arm_lengths):
    """
    Transform the SCARA robot's coordinates from its local frame to the global frame,
    computing joint positions using inverse kinematics.

    :param local_origin: (X, Y) position of the SCARA's local frame origin in the global frame.
    :param robot_base: (X, Y) position of the SCARA arm's base in the global frame.
    :param theta_local: Rotation angle of the local frame compared to the global frame (in degrees, counterclockwise).
    :param end_effector_local: (x, y) position of the end-effector in the local frame.
    :param arm_lengths: (l1, l2) lengths of the first and second links of the arm.
    :return: List of positions [(base_x, base_y), (joint1_x, joint1_y), (end_effector_x, end_effector_y)] in global coordinates.
    """
    # Unpack inputs
    origin_x, origin_y = local_origin
    base_x_global, base_y_global = robot_base
    end_effector_x, end_effector_y = end_effector_local
    l1, l2 = arm_lengths

    # Step 1: Convert robot base to the local frame
    theta_local_rad = math.radians(theta_local)
    base_x_local = (base_x_global - origin_x) * math.cos(-theta_local_rad) - (base_y_global - origin_y) * math.sin(-theta_local_rad)
    base_y_local = (base_x_global - origin_x) * math.sin(-theta_local_rad) + (base_y_global - origin_y) * math.cos(-theta_local_rad)

    # Step 2: Compute inverse kinematics for joint angles
    dx = end_effector_x - base_x_local
    dy = end_effector_y - base_y_local
    r = math.sqrt(dx**2 + dy**2)

    if r > l1 + l2:
        raise ValueError("End-effector position is unreachable.")

    # Theta2 (angle of the second arm relative to the first arm)
    cos_theta2 = (r**2 - l1**2 - l2**2) / (2 * l1 * l2)
    theta2 = math.acos(cos_theta2)

    # Theta1 (angle of the first arm relative to the local frame's X-axis)
    phi = math.atan2(dy, dx)
    beta = math.atan2(l2 * math.sin(theta2), l1 + l2 * math.cos(theta2))
    theta1 = phi - beta

    # Compute the intermediate joint position (local frame)
    joint1_local_x = base_x_local + l1 * math.cos(theta1)
    joint1_local_y = base_y_local + l1 * math.sin(theta1)

    # Step 3: Transform intermediate joint and end-effector to the global frame
    joint1_global_x = origin_x + (joint1_local_x * math.cos(theta_local_rad) - joint1_local_y * math.sin(theta_local_rad))
    joint1_global_y = origin_y + (joint1_local_x * math.sin(theta_local_rad) + joint1_local_y * math.cos(theta_local_rad))
    joint1_global = (joint1_global_x, joint1_global_y)

    end_effector_global_x = origin_x + (end_effector_x * math.cos(theta_local_rad) - end_effector_y * math.sin(theta_local_rad))
    end_effector_global_y = origin_y + (end_effector_x * math.sin(theta_local_rad) + end_effector_y * math.cos(theta_local_rad))
    end_effector_global = (end_effector_global_x, end_effector_global_y)

    return [robot_base, joint1_global, end_effector_global]


def create_rectangle(p1, p2, width):
    """
    Create a rectangle (polygon) given two points (p1, p2) and a width.
    :param p1: (x, y) starting point of the rectangle.
    :param p2: (x, y) ending point of the rectangle.
    :param width: Width of the rectangle.
    :return: Shapely Polygon representing the rectangle.
    """
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    length = math.sqrt(dx**2 + dy**2)

    # Unit vector perpendicular to the line (p1 -> p2)
    perp_x = -dy / length * (width / 2)
    perp_y = dx / length * (width / 2)

    # Four corners of the rectangle
    corners = [
        (p1[0] + perp_x, p1[1] + perp_y),
        (p2[0] + perp_x, p2[1] + perp_y),
        (p2[0] - perp_x, p2[1] - perp_y),
        (p1[0] - perp_x, p1[1] - perp_y)
    ]
    return Polygon(corners)


def check_collision(n_scaras, buffer_size=10):
    """
    Check for collisions between n SCARA robots using buffered rectangular links.

    :param n_scaras: List of dictionaries, each containing:
                     - 'local_origin': (X, Y)
                     - 'robot_base': (X, Y)
                     - 'theta_local': float (degrees)
                     - 'end_effector_local': (x, y)
                     - 'arm_lengths': (l1, l2)
    :param buffer_size: Buffer size to enlarge the polygons (default: 10mm).
    :return: True if any collision is detected, False otherwise.
    """
    link_rectangles = []

    # Transform all SCARA robot positions to global coordinates and create buffered rectangles
    for scara in n_scaras:
        positions = transform_to_global(
            scara['local_origin'],
            scara['robot_base'],
            scara['theta_local'],
            scara['end_effector_local'],
            scara['arm_lengths']
        )

        # Create rectangles for each link and apply buffer
        link1 = create_rectangle(positions[0], positions[1], width=30).buffer(buffer_size)
        link2 = create_rectangle(positions[1], positions[2], width=30).buffer(buffer_size)
        link_rectangles.append((link1, link2))

    # Check for collisions between rectangles from different SCARA arms
    for i in range(len(link_rectangles)):
        for j in range(i + 1, len(link_rectangles)):
            # Extract the two sets of rectangles
            arm1_link1, arm1_link2 = link_rectangles[i]
            arm2_link1, arm2_link2 = link_rectangles[j]

            # Check all combinations of rectangles between the two SCARA arms
            if arm1_link1.intersects(arm2_link1) or \
               arm1_link1.intersects(arm2_link2) or \
               arm1_link2.intersects(arm2_link1) or \
               arm1_link2.intersects(arm2_link2):
                return True  # Collision detected

    return False  # No collision detected


def plot_scaras(n_scaras, buffer_size=10):
    """
    Plot n SCARA robots in the global frame, showing buffered rectangular links.

    :param n_scaras: List of SCARA robots with their parameters.
    :param buffer_size: Buffer size for rectangles (default: 10mm).
    """
    plt.figure(figsize=(10, 10))
    ax = plt.gca()

    for i, scara in enumerate(n_scaras):
        # Get the global positions of the SCARA components
        positions = transform_to_global(
            scara['local_origin'],
            scara['robot_base'],
            scara['theta_local'],
            scara['end_effector_local'],
            scara['arm_lengths']
        )

        # Plot the buffered links
        link1 = create_rectangle(positions[0], positions[1], width=30).buffer(buffer_size)
        link2 = create_rectangle(positions[1], positions[2], width=30).buffer(buffer_size)

        patch1 = patches.Polygon(list(link1.exterior.coords), closed=True, edgecolor='blue', fill=True, alpha=0.3)
        patch2 = patches.Polygon(list(link2.exterior.coords), closed=True, edgecolor='green', fill=True, alpha=0.3)
        ax.add_patch(patch1)
        ax.add_patch(patch2)

        # Plot the joints and end-effector
        x_coords, y_coords = zip(*positions)
        plt.scatter(x_coords[0], y_coords[0], color='red', zorder=5, label=f"Base {i + 1}")
        plt.scatter(x_coords[1], y_coords[1], color='purple', zorder=5, label=f"Joint {i + 1}")
        plt.scatter(x_coords[2], y_coords[2], color='orange', zorder=5, label=f"End-Effector {i + 1}")

    # Add global axes and finalize plot
    plt.axhline(0, color='gray', linestyle='--', linewidth=0.5)
    plt.axvline(0, color='gray', linestyle='--', linewidth=0.5)
    plt.title("SCARA Robots with Buffered Rectangular Links in Global Frame")
    plt.xlabel("X (Global)")
    plt.ylabel("Y (Global)")
    plt.grid()

    # Set equal aspect ratio
    ax.set_aspect('equal', adjustable='box')

    plt.show()


# Example Usage
if __name__ == "__main__":
    # Define n SCARA robots
    n_scaras = [
        {
            'local_origin': (900, 0),
            'robot_base': (950, 150),
            'theta_local': 90,
            'end_effector_local': (290, 10),
            'arm_lengths': (220, 220)
        },
        {
            'local_origin': (600, 300),
            'robot_base': (450, 350),
            'theta_local': 180,
            'end_effector_local': (290, 10),
            'arm_lengths': (220, 220)
        },
    ]

    start_time = time.time()
    collision = check_collision(n_scaras, buffer_size=10)
    end_time = time.time()
    time_taken = end_time - start_time
    print(time_taken)
    print("Collision Detected:" if collision else "No Collision")

    # Plot SCARA robots with buffers
    plot_scaras(n_scaras, buffer_size=10)