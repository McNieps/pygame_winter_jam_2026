import asyncio

from isec.app import App
from game.instances.world_map_instance import WorldMapInstance
from game.instances.combat_instance import CombatInstance
from game.battle_engine.models import Team, Weapon, Modifier, ModifierEffect, EffectType, EventTrigger, EffectTarget, ModifierCondition

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

count_strikes = Modifier(
    name="Relentless Counter",
    description="Increments the shared strike_count on this weapon each time it fires.",
    trigger=EventTrigger.ON_WEAPON_FIRE,
    priority=20,
    effects=[
        ModifierEffect(
            effect_type=EffectType.INCREMENT_WEAPON_COUNTER,
            target=EffectTarget.SELF_WEAPON,
            value_str="strike_count",
        ),
    ],
)

relentless_payoff = Modifier(
    name="Relentless",
    description="On the 8th strike, reset a random enemy weapon's cooldown.",
    trigger=EventTrigger.ON_WEAPON_FIRE,
    priority=10,
    condition=ModifierCondition(attribute="weapon.strike_count", operator="==", value=2),
    effects=[
        ModifierEffect(
            effect_type=EffectType.RESET_WEAPON_COUNTER,
            target=EffectTarget.SELF_WEAPON,
            value_str="strike_count",
        ),
        ModifierEffect(
            effect_type=EffectType.RESET_COOLDOWN,
            target=EffectTarget.RANDOM_ENEMY_WEAPON,
        ),
    ],
)

team_a = Team(
    name="Team A", hp=100, max_hp=100,
    weapons=[Weapon(name="Reactive Blade", base_damage=1, cooldown_ticks_max=20, modifiers=[count_strikes, relentless_payoff], icon="dagger")],
)
team_b = Team(
    name="Team B", hp=100, max_hp=100,
    weapons=[Weapon(name="Predator Axe", base_damage=12, cooldown_ticks_max=50, modifiers=[on_enemy_struck_mod], icon="dagger"),
             Weapon(name="Predator Axe", base_damage=12, cooldown_ticks_max=50, modifiers=[on_enemy_struck_mod], icon="dagger"),
             Weapon(name="Predator Axe", base_damage=12, cooldown_ticks_max=50, modifiers=[on_enemy_struck_mod], icon="dagger")],
)

async def main() -> None:
    App.init("game/assets/")
    await CombatInstance(team_a, team_b).execute()
    # await WorldMapInstance().execute()

asyncio.run(main())
