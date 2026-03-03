import pygame
import numpy as np


def fast_outline(surface: pygame.Surface, outline_color: tuple[int, int, int]) -> None:
    # Lock surface and get direct pixel access
    pixels3d = pygame.surfarray.pixels3d(surface)
    alpha = pygame.surfarray.pixels_alpha(surface)

    # Create mask of non-transparent pixels
    mask = alpha > 0

    # Calculate the outline by looking at neighbors
    # For each pixel, if it's transparent but has a non-transparent neighbor, it should be outlined
    outline_mask = np.zeros_like(mask)

    # Check all neighbors and combine them
    outline_mask[:-1, :] |= mask[1:, :]  # bottom neighbor
    outline_mask[1:, :] |= mask[:-1, :]  # top neighbor
    outline_mask[:, :-1] |= mask[:, 1:]  # right neighbor
    outline_mask[:, 1:] |= mask[:, :-1]  # left neighbor

    # Remove original mask to keep only the outline
    outline_mask &= ~mask

    # Apply the outline color and alpha in one go
    pixels3d[outline_mask] = outline_color
    alpha[outline_mask] = 255

    # Unlock surface
    del pixels3d
    del alpha
