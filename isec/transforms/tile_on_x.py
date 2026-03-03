import pygame


def tile_on_x(source_surface: pygame.Surface,
              x_offset: int,
              goal_width: int):

    src_width, src_height = source_surface.get_size()

    if src_width == 0 or goal_width == 0:
        return pygame.Surface((0, 0), pygame.SRCALPHA)

    x_offset %= src_width
    if x_offset:
        x_offset -= src_width

    dest_surface = pygame.Surface((goal_width, src_height), pygame.SRCALPHA)
    number_of_blit = (goal_width-x_offset)//src_width+1
    for i in range(number_of_blit):
        dest_surface.blit(source_surface, (i * src_width + x_offset, 0))

    return dest_surface
