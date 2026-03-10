import pygame
import numpy as np
import numba


def fake_rotate_x(surface: pygame.Surface,
                  angle_deg: float) -> None:
    fake_rotate_around_x_np(
        pygame.surfarray.pixels3d(surface),
        pygame.surfarray.pixels_alpha(surface),
        angle_deg,
        500
    )


@numba.njit
def fake_rotate_around_x_np(arr: np.ndarray,
                             alpha: np.ndarray,
                             angle_deg: float,
                             nominal_dist: float) -> None:

    angle_rad = np.radians(angle_deg)
    cos_a = np.cos(angle_rad)

    width, height = arr.shape[:2]
    center_x = width / 2
    original = arr.copy()
    original_alpha = alpha.copy()
    arr[:] = 0
    alpha[:] = 0
    for y in range(height):
        row_scale = (np.sin(angle_rad)*y+nominal_dist)/nominal_dist
        src_y = int(y / cos_a)
        for x in range(width):
            src_x = int((x - center_x) * row_scale + center_x)

            if 0 <= src_x < width and 0 <= src_y < height:
                arr[x, y] = original[src_x, src_y]
                alpha[x, y] = original_alpha[src_x, src_y]

# small warmup to avoid surface lock
fake_rotate_x(pygame.Surface((100, 100), pygame.SRCALPHA), 45)
