import pygame  # type: ignore
import random
import math
import time
import numpy
from classButton import Button
from classSlider import Slider

def handle_circle_collisions(circles):
    for i in range(len(circles)):
        circle1 = circles[i]
        r1 = circle1["radius"]
        
        for j in range(i + 1, len(circles)):
            circle2 = circles[j]
            r2 = circle2["radius"]

            # Calculate squared distance between circle centers
            dx = circle2["pos"][0] - circle1["pos"][0]
            dy = circle2["pos"][1] - circle1["pos"][1]
            dist_sq = dx ** 2 + dy ** 2
            radius_sum = r1 + r2
            radius_sum_sq = radius_sum ** 2

            # Check if circles overlap using squared distance
            if dist_sq < radius_sum_sq:
                # Calculate overlap distance
                distance = math.sqrt(dist_sq)
                overlap = radius_sum - distance
                
                # Avoid repeated division by distance in adjustments
                if distance > 0:
                    inv_distance = 1 / distance
                    move_x = dx * inv_distance * (overlap / 2)
                    move_y = dy * inv_distance * (overlap / 2)

                    # Adjust positions to resolve overlap
                    circle1["pos"][0] -= move_x
                    circle1["pos"][1] -= move_y
                    circle2["pos"][0] += move_x
                    circle2["pos"][1] += move_y

                # Unit vectors in normal and tangent directions
                un = [dx * inv_distance, dy * inv_distance]
                ut = [-dy * inv_distance, dx * inv_distance]

                # Normal and tangential components of the velocities
                v1n = numpy.dot(un, circle1["vel"])
                v1t = numpy.dot(ut, circle1["vel"])
                v2n = numpy.dot(un, circle2["vel"])
                v2t = numpy.dot(ut, circle2["vel"])

                # Conservation of momentum for elastic collision
                m1, m2 = circle1["mass"], circle2["mass"]
                v1n_prime = (v1n * (m1 - m2) + 2 * m2 * v2n) / (m1 + m2)
                v2n_prime = (v2n * (m2 - m1) + 2 * m1 * v1n) / (m1 + m2)

                # Convert normal and tangential velocities to vectors
                V1n = [v1n_prime * un[0], v1n_prime * un[1]]
                V1t = [v1t * ut[0], v1t * ut[1]]
                V2n = [v2n_prime * un[0], v2n_prime * un[1]]
                V2t = [v2t * ut[0], v2t * ut[1]]

                # Final velocities after collision
                circle1["vel"][0] = V1n[0] + V1t[0]
                circle1["vel"][1] = V1n[1] + V1t[1]
                circle2["vel"][0] = V2n[0] + V2t[0]
                circle2["vel"][1] = V2n[1] + V2t[1]
                
                # Reflect velocities, basic not correct
                #circle1["vel"][0], circle2["vel"][0] = circle2["vel"][0], circle1["vel"][0]
                #circle1["vel"][1], circle2["vel"][1] = circle2["vel"][1], circle1["vel"][1]

# Hard border collision check
def handle_border_collision(circles):
    for circle in circles:
        if circle["pos"][0] < circle["radius"] + border_thickness:
            circle["pos"][0] = circle["radius"] + border_thickness
            circle["vel"][0] *= -0.95
        elif circle["pos"][0] > simulation_width - circle["radius"] - border_thickness:
            circle["pos"][0] = simulation_width - circle["radius"] - border_thickness
            circle["vel"][0] *= -0.95

        if circle["pos"][1] < circle["radius"] + border_thickness:
            circle["pos"][1] = circle["radius"] + border_thickness
            circle["vel"][1] *= -0.95
        elif circle["pos"][1] > height - circle["radius"] - border_thickness:
            circle["pos"][1] = height - circle["radius"] - border_thickness
            circle["vel"][1] *= -0.95

def find_closest_circles(circles, reference_circle, num_closest):
    distances = [(math.hypot(c["pos"][0] - reference_circle["pos"][0], c["pos"][1] - reference_circle["pos"][1]), c) for c in circles if c != reference_circle]
    distances.sort()
    return [circle for _, circle in distances[:num_closest]]

# Function to calculate radius based on mass
def calculate_radius(mass):
    # Map mass from 0.5-1.5 to radius range 5-15 and ensures that the radius is within bounds 5 to 15
    return min(max(int((mass - 0.5) * 10) + 5, 5), 15)  

# Initialize Pygame
pygame.init()
simulation_width, slider_column_width, height = 900, 300, 600
window = pygame.display.set_mode((simulation_width + slider_column_width, height))
pygame.display.set_caption("Moving Circles with Force and Multiple Sliders")
background_color = (0x00, 0x79, 0x91)
circle_color = (0xDB, 0x50, 0x4A)
WHITE, BLACK = (255, 255, 255), (0, 0, 0)
CIRCLE_RADIUS, num_circles = 15, 30
circles = []

# Initialize variables for frame time calculation
frame_time = 0


for _ in range(num_circles):
    while True:
        x = random.randint(CIRCLE_RADIUS, simulation_width - CIRCLE_RADIUS)
        y = random.randint(CIRCLE_RADIUS, height - CIRCLE_RADIUS)
        vx, vy = random.uniform(-2, 2), random.uniform(-2, 2)
        phase = random.uniform(0, 2 * math.pi)
        mass = 1 + 0.5 * math.sin(phase)

        # If there's no overlap, add the circle and break the loop
        if not any(math.hypot(x - c["pos"][0], y - c["pos"][1]) < 2 * CIRCLE_RADIUS + 1 for c in circles):
            circles.append({"pos": [x, y], "vel": [vx, vy], "force": [0, 0], "mass": mass, "phase": phase, "radius": CIRCLE_RADIUS})
            break

# Create buttons for reset and stop/resume
reset_button = Button(simulation_width + 20, 50, slider_column_width - 40, 30, "Reset")
toggle_button = Button(simulation_width + 20, 90, slider_column_width - 40, 30, "Stop/Resume")

# Default force properties
timestep = 1.0  # Initial timestep
distance_slider = 20  # Distance where attraction or repulsion changes
gravitational_constant = 4  # Strength of gravitational constant between circles
repulsion_strength = 2  # Strength of repulsive force when circles come too close
num_closest = 4

# Create sliders for timestep, gravity, and max speed
sliders = [
    Slider(simulation_width + 20, 170, slider_column_width - 40, "Timestep", 0.1, 5.0, timestep),
    Slider(simulation_width + 20, 240, slider_column_width - 40, "distance_slider", 0.0, 40, distance_slider),
    Slider(simulation_width + 20, 310, slider_column_width - 40, "gravitational_constant", 0.0, 5, gravitational_constant),
    Slider(simulation_width + 20, 380, slider_column_width - 40, "repulsion_strength", 0.0, 5, repulsion_strength),
    Slider(simulation_width + 20, 450, slider_column_width - 40, "num_closest", 0, 5, num_closest),
    Slider(simulation_width + 20, 520, slider_column_width - 40, "Number of Circles", 1, 50, num_circles) 
]

# Main loop
running = True
clock = pygame.time.Clock()
is_dragging = False
is_running = True

while running:
    frame_start_time = time.time()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if reset_button.is_clicked(event.pos):
                for c in circles:
                    c["pos"] = [random.randint(CIRCLE_RADIUS, simulation_width - CIRCLE_RADIUS), random.randint(CIRCLE_RADIUS, height - CIRCLE_RADIUS)]
                    c["vel"] = [random.uniform(-2, 2), random.uniform(-2, 2)]
            elif toggle_button.is_clicked(event.pos):
                is_running = not is_running  # Toggle running state
            is_dragging = next((i for i, s in enumerate(sliders) if s.rect.collidepoint(event.pos)), None)
        elif event.type == pygame.MOUSEBUTTONUP:
            is_dragging = None
        elif event.type == pygame.MOUSEMOTION and is_dragging is not None:
            sliders[is_dragging].update(event.pos)

    # Update sliders' values
    timestep = sliders[0].value
    distance_slider = sliders[1].value
    gravitational_constant = sliders[2].value
    repulsion_strength = sliders[3].value
    new_num_circles = int(sliders[5].value)
    num_closest = int(sliders[4].value)
    
    # Fill background
    window.fill(background_color)

    # Draw hard border around the simulation area
    border_thickness = 5
    pygame.draw.rect(window, BLACK, (0, 0, simulation_width, height), border_thickness)

     # Adjust the circles array to match the slider value
    if new_num_circles != len(circles):
        if new_num_circles > len(circles):
            for _ in range(new_num_circles - len(circles)):
                # Add new circles
                while True:
                    x = random.randint(CIRCLE_RADIUS, simulation_width - CIRCLE_RADIUS)
                    y = random.randint(CIRCLE_RADIUS, height - CIRCLE_RADIUS)
                    vx, vy = random.uniform(-2, 2), random.uniform(-2, 2)
                    phase = random.uniform(0, 2 * math.pi)
                    mass = 1 + 0.5 * math.sin(phase)

                    # Ensure the new circle doesn't overlap with existing ones
                    if not any(math.hypot(x - c["pos"][0], y - c["pos"][1]) < 2 * CIRCLE_RADIUS + 1 for c in circles):
                        circles.append({"pos": [x, y], "vel": [vx, vy], "force": [0, 0], "mass": mass, "phase": phase, "radius": CIRCLE_RADIUS})
                        break
        else:
            # Remove excess circles
            circles = circles[:new_num_circles]

    # Update circle positions and check for collisions only if running
    if is_running:
        for i, circle in enumerate(circles):
            # Update mass with sinusoidal oscillation around 1, between 0.5 and 1.5
            circle["mass"] = 1 + 0.5 * math.sin(frame_start_time + circle["phase"])
            # Update radius based on mass
            circle["radius"] = calculate_radius(circle["mass"])
            # Reset the force
            circle["force"] = [0, 0]

            # Calculate forces based on distances to other circles
            for other in circles:
                if circle is not other:
                    dx, dy = other["pos"][0] - circle["pos"][0], other["pos"][1] - circle["pos"][1]
                    distance = math.hypot(dx, dy) + 1e-10
                    force = (gravitational_constant * circle["mass"] * other["mass"] / distance**2) - (repulsion_strength / distance if distance < distance_slider else 0)
                    circle["force"][0] += dx / distance * force
                    circle["force"][1] += dy / distance * force
            # Update velocity based on acceleration and timestep
            circle["vel"] = [v + f / circle["mass"] * timestep for v, f in zip(circle["vel"], circle["force"])]
            # Update position based on velocity and timestep
            circle["pos"] = [p + v * timestep for p, v in zip(circle["pos"], circle["vel"])]
        
        # Check for border collisions
        handle_border_collision(circles)

        # Check for collisions between circles
        handle_circle_collisions(circles)

    # Create a set to track drawn lines
    drawn_lines = set()
    
    # Draw lines between the four closest circles to each circle
    for circle in circles:
        closest_circles = find_closest_circles(circles, circle, num_closest)
        for closest_circle in closest_circles:
            # Create a tuple of the points to ensure direction
            line_tuple = (tuple(circle["pos"]), tuple(closest_circle["pos"]))
          
            # Draw the line only if it hasn't been drawn before
            if line_tuple not in drawn_lines:
                pygame.draw.line(window, WHITE, circle["pos"], closest_circle["pos"], 1)
                drawn_lines.add(line_tuple)
    
    for circle in circles:
        pygame.draw.circle(window, circle_color, [int(v) for v in circle["pos"]], circle["radius"])
    for button in [reset_button, toggle_button]:
        button.draw(window)
    for slider in sliders:
        slider.draw(window)
    
    # Draw Frame Time above buttons
    font = pygame.font.SysFont(None, 24)
    frame_time_text = font.render(f"Frame Time: {frame_time * 1000:.2f} ms", True, WHITE)
    window.blit(frame_time_text, (simulation_width + 20, 10))
    
    # # Draw the circle
    # for circle in circles:
    #     pygame.draw.circle(window, circle_color, (int(circle["pos"][0]), int(circle["pos"][1])), circle["radius"])

    # # Draw buttons
    # reset_button.draw(window)
    # toggle_button.draw(window, hover=toggle_button.is_clicked(pygame.mouse.get_pos()))

    # # Draw each slider
    # for slider in sliders:
    #     slider.draw(window)

    # Calculate frame time in seconds and update the display
    frame_time = time.time() - frame_start_time  # Time taken for one cycle in seconds
    pygame.display.flip()
    clock.tick(60)  # Limit to 60 FPS

# Quit Pygame
pygame.quit()
