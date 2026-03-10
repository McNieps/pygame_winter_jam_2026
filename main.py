import asyncio

from isec.app import App
from game.instances.world_map_instance import WorldMapInstance
from game.instances.combat_instance import CombatInstance

async def main() -> None:
    App.init("game/assets/")
    await CombatInstance().execute()
    # await WorldMapInstance().execute()

asyncio.run(main())
