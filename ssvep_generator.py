import argparse
import math
import time

import pygame

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "SSVEP circular checkerboard stimuli generator (frame-locked). "
            "Frequencies are realized by toggling patterns every N frames at a fixed FPS."
        )
    )
    p.add_argument("--fullscreen", action="store_true", help="Run fullscreen")
    p.add_argument("--width", type=int, default=None, help="Window width (ignored if --fullscreen)")
    p.add_argument("--height", type=int, default=None, help="Window height (ignored if --fullscreen)")
    p.add_argument("--fps", type=int, default=60, help="Target FPS used for frame locking (default: 60)")

    p.add_argument("--radius", type=int, default=100, help="Outer radius of the circular checkerboard")
    p.add_argument("--segments", type=int, default=18, help="Number of angular segments per ring")

    p.add_argument("--freq-up", type=float, default=7.5)
    p.add_argument("--freq-down", type=float, default=8.57)
    p.add_argument("--freq-left", type=float, default=10.0)
    p.add_argument("--freq-right", type=float, default=12.0)

    p.add_argument(
        "--auto-switch",
        action="store_true",
        help="Enable auto-switch on startup (press 'A' to toggle while running)",
    )
    p.add_argument(
        "--switch-duration",
        type=float,
        default=60.0,
        help="Auto-switch duration in seconds (default: 60)",
    )

    return p.parse_args()

def draw_red_cross(screen: pygame.Surface, center: tuple[int, int]) -> None:
    RED = (255, 0, 0)
    cross_width = 5
    cross_length = 12
    cx, cy = center

    pygame.draw.rect(
        screen,
        RED,
        (cx - cross_width // 2, cy - cross_length, cross_width, cross_length * 2),
    )
    pygame.draw.rect(
        screen,
        RED,
        (cx - cross_length, cy - cross_width // 2, cross_length * 2, cross_width),
    )

def draw_checkerboard(
    screen: pygame.Surface,
    center: tuple[int, int],
    radius: int,
    start_white: bool,
    num_segments: int,
) -> None:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)

    angle_step = 2 * math.pi / num_segments
    for i in range(num_segments):
        color = WHITE if ((i % 2 == 0) == start_white) else BLACK

        start_angle = i * angle_step
        end_angle = start_angle + angle_step
        points = [
            center,
            (center[0] + radius * math.cos(start_angle), center[1] + radius * math.sin(start_angle)),
            (center[0] + radius * math.cos(end_angle), center[1] + radius * math.sin(end_angle)),
            center,
        ]
        pygame.draw.polygon(screen, color, points)

def quantize_half_period_frames(fps: int, freq_hz: float) -> int:
    """Return integer frames per half-period for a square-wave flicker.

    We toggle at half-period boundaries, so the toggle interval is fps/(2*freq).
    Rounding makes the produced frequency stable but slightly approximate.
    """
    if freq_hz <= 0:
        raise ValueError("Frequency must be > 0")
    frames = int(round(fps / (2.0 * freq_hz)))
    return max(frames, 1)

def main() -> None:
    args = parse_args()

    pygame.init()

    # Determine window size
    if args.fullscreen:
        display_info = pygame.display.Info()
        width, height = display_info.current_w, display_info.current_h
        flags = pygame.FULLSCREEN
    else:
        display_info = pygame.display.Info()
        width = args.width or display_info.current_w
        height = args.height or display_info.current_h
        flags = 0

    screen = pygame.display.set_mode((width, height), flags)
    pygame.display.set_caption("SSVEP Circular Checkerboard Stimulation (frame-locked)")

    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)

    # Frequencies (Hz)
    frequencies = {
        "up": float(args.freq_up),
        "down": float(args.freq_down),
        "left": float(args.freq_left),
        "right": float(args.freq_right),
    }

    # Pre-compute frame toggle intervals (half-period)
    toggle_every_n_frames = {
        k: quantize_half_period_frames(args.fps, f) for k, f in frequencies.items()
    }

    # Pattern states
    pattern_states = {key: True for key in frequencies.keys()}
    frame_counters = {key: 0 for key in frequencies.keys()}

    # Circle center positions based on actual window size
    circle_centers = {
        "up": (width // 2, height // 8),
        "down": (width // 2, 7 * height // 8),
        "left": (width // 8, height // 2),
        "right": (7 * width // 8, height // 2),
    }

    # Shape switching
    shapes = ["red_cross", "up", "right", "down", "left"]
    current_shape_index = 0

    auto_switch = bool(args.auto_switch)
    switch_duration = float(args.switch_duration)
    last_switch_time = time.perf_counter()

    # Optional text overlay
    font = pygame.font.Font(None, 28)

    clock = pygame.time.Clock()
    running = True

    while running:
        now = time.perf_counter()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    current_shape_index = (current_shape_index + 1) % len(shapes)
                elif event.key == pygame.K_a:
                    auto_switch = not auto_switch
                    last_switch_time = now
                elif event.key == pygame.K_f:
                    # Toggle fullscreen (simple restart of display mode)
                    args.fullscreen = not args.fullscreen
                    if args.fullscreen:
                        di = pygame.display.Info()
                        width, height = di.current_w, di.current_h
                        screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
                    else:
                        di = pygame.display.Info()
                        width = args.width or di.current_w
                        height = args.height or di.current_h
                        screen = pygame.display.set_mode((width, height))
                    circle_centers = {
                        "up": (width // 2, height // 8),
                        "down": (width // 2, 7 * height // 8),
                        "left": (width // 8, height // 2),
                        "right": (7 * width // 8, height // 2),
                    }

        # Auto-switch
        if auto_switch and (now - last_switch_time >= switch_duration):
            current_shape_index = (current_shape_index + 1) % len(shapes)
            last_switch_time = now

        # Frame-locked toggles: advance counters once per rendered frame
        for direction in pattern_states.keys():
            frame_counters[direction] += 1
            if frame_counters[direction] >= toggle_every_n_frames[direction]:
                pattern_states[direction] = not pattern_states[direction]
                frame_counters[direction] = 0

        # Draw
        screen.fill(BLACK)
        current_shape = shapes[current_shape_index]

        if current_shape == "red_cross":
            draw_red_cross(screen, (width // 2, height // 2))
            overlay = "Mode: fixation (SPACE to cycle) | A: autoswitch | F: fullscreen | ESC: quit"
        else:
            center = circle_centers[current_shape]
            # Multi-ring look
            draw_checkerboard(screen, center, args.radius, pattern_states[current_shape], args.segments)
            draw_checkerboard(screen, center, 3 * args.radius // 4, not pattern_states[current_shape], args.segments)
            draw_checkerboard(screen, center, args.radius // 2, pattern_states[current_shape], args.segments)
            draw_checkerboard(screen, center, args.radius // 4, not pattern_states[current_shape], args.segments)

            # Report realized frequency based on quantization
            n = toggle_every_n_frames[current_shape]
            realized = args.fps / (2.0 * n)
            overlay = (
                f"Target: {current_shape} | f_target={frequencies[current_shape]:.2f}Hz "
                f"f_real≈{realized:.2f}Hz (fps={args.fps}, toggle every {n} frames) | "
                "SPACE cycle | A autoswitch | F fullscreen | ESC quit"
            )

        text = font.render(overlay, True, WHITE)
        screen.blit(text, (12, 12))

        pygame.display.flip()
        clock.tick(args.fps)

    pygame.quit()


if __name__ == "__main__":
    main()
