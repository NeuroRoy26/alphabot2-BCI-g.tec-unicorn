import pygame
import time
import threading
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SSVEP Circular Checkerboard Stimulation")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Frequencies (Hz)
frequencies = {
    "up": 7.5,  # Frequency for the upper pattern
    "down": 8.57,  # Frequency for the lower pattern
    "left": 10,  # Frequency for the left pattern
    "right": 12  # Frequency for the right pattern
}

# Circle center positions
circle_centers = {
    "up": (WIDTH // 2, HEIGHT // 8),
    "down": (WIDTH // 2, 7 * HEIGHT // 8),
    "left": (WIDTH // 8, HEIGHT // 2),
    "right": (7 * WIDTH // 8, HEIGHT // 2)
}

# Circle radius
circle_radius = 100

# Number of segments in the circular checkerboard
num_segments = 18  # Increase for finer patterns

# Pattern states (True for starting with white, False for starting with black)
pattern_states = {key: True for key in frequencies.keys()}

# Last toggle times for each direction
last_toggle_times = {key: time.perf_counter() for key in frequencies.keys()}

# Toggle pattern state for a given direction
def toggle_pattern(direction):
    pattern_states[direction] = not pattern_states[direction]

# Update patterns at their respective frequencies
def update_patterns():
    while running:
        current_time = time.perf_counter()
        for direction, freq in frequencies.items():
            if current_time - last_toggle_times[direction] >= 1 / (2 * freq):
                toggle_pattern(direction)
                last_toggle_times[direction] = current_time
        time.sleep(0.005)  # Reduce CPU usage

# Draw red cross
def draw_red_cross():
    cross_width = 5
    cross_length = 10
    center_x, center_y = WIDTH // 2, HEIGHT // 2

    # Draw vertical part of the cross
    pygame.draw.rect(
        screen, RED,
        (center_x - cross_width // 2, center_y - cross_length, cross_width, cross_length * 2)
    )

    # Draw horizontal part of the cross
    pygame.draw.rect(
        screen, RED,
        (center_x - cross_length, center_y - cross_width // 2, cross_length * 2, cross_width)
    )

# Draw circular checkerboard patterns
def draw_checkerboard(center, radius, start_white):
    angle_step = 2 * math.pi / num_segments
    for i in range(num_segments):
        # Determine color
        color = WHITE if (i % 2 == 0) == start_white else BLACK

        # Calculate wedge coordinates
        start_angle = i * angle_step
        end_angle = start_angle + angle_step
        points = [
            center,
            (center[0] + radius * math.cos(start_angle), center[1] + radius * math.sin(start_angle)),
            (center[0] + radius * math.cos(end_angle), center[1] + radius * math.sin(end_angle)),
            center  # Ensure closure of the segment
        ]

        # Draw the wedge
        pygame.draw.polygon(screen, color, points)

# State for shape switching
shapes = ["red_cross", "up", "right", "down", "left"]
current_shape_index = 0

# Auto-switch feature
auto_switch = False
switch_duration = 60  # Duration in seconds for auto-switch
last_switch_time = time.perf_counter()

# Run update_patterns in a separate thread
running = True
thread = threading.Thread(target=update_patterns, daemon=True)
thread.start()

# Main Pygame loop
try:
    clock = pygame.time.Clock()
    while running:
        current_time = time.perf_counter()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Switch to the next shape
                    current_shape_index = (current_shape_index + 1) % len(shapes)
                elif event.key == pygame.K_a:  # Press 'A' to toggle auto-switch
                    auto_switch = not auto_switch

        # Auto-switch logic
        if auto_switch and (current_time - last_switch_time >= switch_duration):
            current_shape_index = (current_shape_index + 1) % len(shapes)
            last_switch_time = current_time

        # Fill the screen with black
        screen.fill(BLACK)

        # Draw the current shape
        current_shape = shapes[current_shape_index]
        if current_shape == "red_cross":
            draw_red_cross()
        elif current_shape in circle_centers:
            center = circle_centers[current_shape]
            draw_checkerboard(center, circle_radius, pattern_states[current_shape])
            draw_checkerboard(center, 3 * circle_radius // 4, not pattern_states[current_shape])
            draw_checkerboard(center, circle_radius // 2, pattern_states[current_shape])
            draw_checkerboard(center, circle_radius // 4, not pattern_states[current_shape])

        # Update the display
        pygame.display.flip()

        # Limit frame rate
        clock.tick(60)
finally:
    running = False
    thread.join()
