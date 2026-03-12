import asyncio

from isec.app import App
from game.instances.world_map_instance import WorldMapInstance
from game.instances.combat_instance import CombatInstance
from game.battle_engine.models import Team, Weapon, Modifier, ModifierEffect, EffectType, EventTrigger, EffectTarget

on_struck_mod = Modifier(
    name="Reactive Edge",
    description="When MY team is struck, reduce this weapon's cooldown by 20%",
    trigger=EventTrigger.ON_PLAYER_STRUCK,
    priority=10,
    icon="eye",
    effects=[
        ModifierEffect(
            effect_type=EffectType.REDUCE_COOLDOWN,
            target=EffectTarget.SELF_WEAPON,
            value=5,
        )
    ],
)

on_enemy_struck_mod = Modifier(
    name="Predator's Rhythm",
    description="When the ENEMY is struck, reduce this weapon's cooldown by 20%",
    trigger=EventTrigger.ON_ENEMY_STRUCK,
    priority=10,
    icon="eye",
    effects=[
        ModifierEffect(
            effect_type=EffectType.REDUCE_COOLDOWN,
            target=EffectTarget.SELF_WEAPON,
            value=3,
        )
    ],
)

team_a = Team(
    name="Team A", hp=100, max_hp=100,
    weapons=[Weapon(name="Reactive Blade", base_damage=15, cooldown_ticks_max=20, modifiers=[on_struck_mod], icon="dagger")],
)
team_b = Team(
    name="Team B", hp=100, max_hp=100,
    weapons=[Weapon(name="Predator Axe", base_damage=12, cooldown_ticks_max=12, modifiers=[on_enemy_struck_mod], icon="dagger")],
)

async def main() -> None:
    App.init("game/assets/")
    await CombatInstance(team_a, team_b).execute()
    # await WorldMapInstance().execute()

asyncio.run(main())
