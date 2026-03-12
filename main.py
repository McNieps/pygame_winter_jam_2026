import asyncio

from isec.app import App
from game.instances.world_map_instance import WorldMapInstance
from game.instances.combat_instance import CombatInstance
from game.battle_engine.models import Team, Weapon, Modifier, ModifierEffect, EffectType, EventTrigger, EffectTarget

on_struck_mod = Modifier(
    name="Reactive Edge",
    icon="eye",
    description="When struck, reduce this weapon's cooldown by 20%",
    trigger=EventTrigger.ON_PLAYER_STRUCK,
    priority=10,
    effects=[
        ModifierEffect(
            effect_type=EffectType.REDUCE_COOLDOWN,
            target=EffectTarget.SELF_WEAPON,
            value=0.20,
        )
    ],
)

team_a = Team(
    name="Team A",
    hp=100,
    max_hp=100,
    weapons=[
        Weapon(
            name="Fast Blade",
            icon="dagger",
            base_damage=15,
            cooldown_ticks_max=10,
            modifiers=[on_struck_mod],
        ),
    ],
)

team_b = Team(
    name="Team B",
    hp=100,
    max_hp=100,
    weapons=[
        Weapon(
            icon="iron_bar",
            name="Heavy Hammer",
            base_damage=25,
            cooldown_ticks_max=15,
        )
    ],
)


async def main() -> None:
    App.init("game/assets/")
    await CombatInstance(team_a, team_b).execute()
    # await WorldMapInstance().execute()

asyncio.run(main())
