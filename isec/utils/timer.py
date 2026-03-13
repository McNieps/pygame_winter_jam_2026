import typing
import pygame

from isec.environment import Entity, Sprite


class Timer(Entity):
    def __init__(self,
                 callback: typing.Callable[[], None],
                 goal_time: float) -> None:

        super().__init__((0, 0), Sprite(pygame.Surface((0, 0))))
        self.elapsed_time = 0
        self.goal_time = goal_time
        self.callback = callback

    def update(self,
               delta: float) -> None:
        self.elapsed_time += delta
        if self.elapsed_time >= self.goal_time:
            self.callback()
            self.destroy()

class AsyncTimer(Entity):
    def __init__(self,
                 callback,
                 goal_time: float) -> None:

        super().__init__((0, 0), Sprite(pygame.Surface((0, 0))))
        self.elapsed_time = 0
        self.goal_time = goal_time
        self.callback = callback

    async def update(self,
               delta: float) -> None:
        self.elapsed_time += delta
        if self.elapsed_time >= self.goal_time:
            await self.callback()
            self.destroy()
