import math
import pygame


def apply_pie_mask(surface: pygame.Surface, progression: float, angle_offset: float, clockwise: bool = True) -> None:
    """
    Covers a surface with transparency in a pie/clock-wipe pattern.
    - progression=0: fully covered
    - progression=1: fully visible
    - angle_offset: rotates the start angle (in degrees)
    - clockwise: if True, wipe goes clockwise; if False, counterclockwise
    """
    if progression >= 1.0:
        return
    if progression <= 0.0:
        surface.fill((0, 0, 0, 0))
        return

    w, h = surface.get_size()
    cx, cy = w / 2, h / 2
    r = math.sqrt(cx ** 2 + cy ** 2) + 1

    covered_angle = (1.0 - progression) * 2 * math.pi
    start = math.radians(angle_offset) - math.pi / 2  # 12 o'clock default

    if clockwise:
        end = start + covered_angle
    else:
        end = start - covered_angle

    NUM_STEPS = 64
    points = [(cx, cy)]
    for i in range(NUM_STEPS + 1):
        a = start + (end - start) * i / NUM_STEPS
        points.append((cx + math.cos(a) * r, cy + math.sin(a) * r))

    pygame.draw.polygon(surface, (0, 0, 0, 0), points)

