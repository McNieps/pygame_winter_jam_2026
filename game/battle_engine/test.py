"""
Example: Two teams fight. Team A has a modifier:
  "When player is struck, reduce this weapon's cooldown by 20%"
"""

from game.battle_engine import (
    BattleEngine, BattleState, Team, Weapon, Modifier, ModifierEffect,
    EventTrigger, EffectType, EffectTarget,
)

# --- Build modifier ---
on_struck_mod = Modifier(
    name="Reactive Edge",
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

# --- Build teams ---
team_a = Team(
    name="Team A",
    hp=100,
    max_hp=100,
    weapons=[
        Weapon(
            name="Dagger",
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
            name="Heavy Hammer",
            base_damage=25,
            cooldown_ticks_max=15,
        )
    ],
)

# --- Run battle ---
engine = BattleEngine()
state = BattleState(team_a=team_a, team_b=team_b)

all_events = []
while not state.is_over and state.tick < 500:
    state, events = engine.tick(state)
    all_events.extend(events)

    for e in events:
        print(f"  [{e.tick:>3}] {e.type:<26} {e.model_dump_json()}")

print(f"\nBattle over at tick {state.tick}. Winner: {state.winner_id}")

# --- Serialize full state to JSON ---
snapshot = state.model_dump_json(indent=2)
print("\n--- State snapshot (truncated) ---")
print(snapshot[:500], "...")

# --- Deserialize ---
restored = BattleState.model_validate_json(snapshot)
print(f"\nRestored state tick: {restored.tick}, is_over: {restored.is_over}")
