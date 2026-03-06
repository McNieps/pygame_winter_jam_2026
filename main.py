import asyncio

from isec.app import App
from game.instances.world_map_instance import WorldMapInstance


async def main() -> None:
    App.init("game/assets/")
    await WorldMapInstance().execute()

asyncio.run(main())
