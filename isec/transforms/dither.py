import numpy as np
import pygame


def generate_bayer_matrix(power):
    if power < 1:
        raise ValueError("Power must be at least 1")
    matrix = np.array([[0, 2], [3, 1]], dtype=np.float64)
    for p in range(2, power + 1):
        prev_size = matrix.shape[0]
        new_size = prev_size * 2
        new_matrix = np.zeros((new_size, new_size), dtype=np.float64)
        new_matrix[:prev_size, :prev_size] = 4 * matrix
        new_matrix[:prev_size, prev_size:] = 4 * matrix + 2
        new_matrix[prev_size:, :prev_size] = 4 * matrix + 3
        new_matrix[prev_size:, prev_size:] = 4 * matrix + 1
        matrix = new_matrix
    matrix /= (4 ** power)
    return matrix


bayer_matrix = generate_bayer_matrix(4)


def dither(surface, progression):
    progression = np.clip(progression, 0.0, 1.0)
    width, height = surface.get_size()
    bayer_size = bayer_matrix.shape[0]

    y, x = np.ogrid[:height, :width]
    mask = (progression > bayer_matrix[y % bayer_size, x % bayer_size])

    mask_alpha = mask.T

    alpha_array = pygame.surfarray.pixels_alpha(surface)
    alpha_array[:] *= mask_alpha
    del alpha_array

    return surface


if __name__ == '__main__':
    import time

    pygame.init()

    test_surface = pygame.Surface((300, 200), pygame.SRCALPHA)
    test_surface.fill((255, 100, 100))

    dither_progression = 0.153+0.5

    t = time.time()
    for _ in range(1000):
        dithered_surface = dither(test_surface, dither_progression)
    print(time.time()-t)

    pygame.image.save(dithered_surface, "dithered_image.png")
