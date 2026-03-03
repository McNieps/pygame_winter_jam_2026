import asyncio
import pygame
import numpy
import yaml
import _cffi_backend

from isec.app import App
from game.instances.game_instance import GameInstance


async def main() -> None:
    App.init("game/assets/")
    await GameInstance().execute()

asyncio.run(main())
