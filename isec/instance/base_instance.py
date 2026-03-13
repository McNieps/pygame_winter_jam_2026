import pygame
import asyncio

import isec.app
from isec.app.resource import Resource
from isec.instance.handlers import LoopHandler, EventHandler


class BaseInstance:
    def __init__(self):
        instance_dict: dict = Resource.data["instance"][self.__class__.__name__]

        fps = instance_dict.get("fps", Resource.data["instance"]["default"]["fps"])
        key_dict = instance_dict["controls"]

        try:
            key_dict.update(Resource.data["instance"]["BaseInstance"])
        except KeyError:
            pass

        self.event_handler = EventHandler(key_dict)
        self.event_handler.register_quit_callback(LoopHandler.stop_game)
        self.window = isec.app.App.window
        self.fps = fps

    async def _preloop(self):
        pygame.display.flip()
        LoopHandler.limit_and_get_delta(self.fps)
        await self.event_handler.handle_all()

    async def setup(self):
        return

    async def loop(self):
        return

    async def finish(self):
        return

    async def execute(self):
        await self.setup()
        LoopHandler.stack.append(self)

        while LoopHandler.is_running(self):
            await self._preloop()
            await self.loop()
            await asyncio.sleep(0)

        await self.finish()

    @property
    def delta(self):
        return LoopHandler.delta
