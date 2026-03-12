from enum import Enum
from typing import Any
from pydantic import BaseModel, Field
import uuid


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class EventTrigger(str, Enum):
    """All possible triggers a modifier can listen to."""
    ON_TICK           = "on_tick"
    ON_WEAPON_FIRE    = "on_weapon_fire"
    ON_DAMAGE_DEALT   = "on_damage_dealt"
    ON_DAMAGE_TAKEN   = "on_damage_taken"
    ON_WEAPON_HIT     = "on_weapon_hit"       # Projectile/attack connected
    ON_PLAYER_STRUCK  = "on_player_struck"    # Owner's team took a hit
    ON_ENEMY_STRUCK   = "on_enemy_struck"     # Opposing team took a hit
    ON_KILL           = "on_kill"
    ON_BATTLE_START   = "on_battle_start"
    ON_MODIFIER_STATE = "on_modifier_state"   # Another modifier changed state


class EffectType(str, Enum):
    """What a modifier effect does when triggered."""
    REDUCE_COOLDOWN      = "reduce_cooldown"   # value = multiplier (0.2 = -20%)
    SET_COOLDOWN         = "set_cooldown"      # value = absolute ticks
    MULTIPLY_DAMAGE      = "multiply_damage"   # value = multiplier
    ADD_DAMAGE           = "add_damage"        # value = flat amount
    HEAL                 = "heal"              # value = flat amount
    APPLY_STATUS         = "apply_status"      # value = status name
    REMOVE_STATUS        = "remove_status"     # value = status name
    INCREMENT_COUNTER    = "increment_counter" # Modifier internal state
    RESET_COUNTER        = "reset_counter"
    RESET_COOLDOWN            = "reset_cooldown"            # Set cooldown_ticks_current to 0 (full penalty)
    INCREMENT_WEAPON_COUNTER  = "increment_weapon_counter"  # value_str = key in weapon.custom_state
    RESET_WEAPON_COUNTER      = "reset_weapon_counter"      # value_str = key in weapon.custom_state


class EffectTarget(str, Enum):
    """Who/what the effect applies to."""
    SELF_WEAPON          = "self_weapon"          # Weapon this modifier is attached to
    ALL_ALLY_WEAPONS     = "all_ally_weapons"
    ENEMY_TEAM           = "enemy_team"
    TRIGGERING_WEAPON    = "triggering_weapon"    # The weapon that caused the event
    RANDOM_ENEMY_WEAPON  = "random_enemy_weapon"  # One random enemy weapon (seeded RNG)


# ---------------------------------------------------------------------------
# Modifier definition (data-driven, fully serializable)
# ---------------------------------------------------------------------------

class ModifierEffect(BaseModel):
    """A single atomic effect produced when a modifier fires."""
    effect_type: EffectType
    target: EffectTarget
    value: float = 0.0
    value_str: str = ""  # For string-based effects (e.g. status names)


class ModifierCondition(BaseModel):
    """Optional condition that must be true for the modifier to fire."""
    # e.g. "counter >= 3", "target_hp_pct < 0.5"
    attribute: str          # e.g. "counter", "target_hp_pct"
    operator: str           # ">=", "<=", "==", ">", "<"
    value: float


class Modifier(BaseModel):
    """
    A data-driven modifier. Fully serializable.
    Logic is interpreted by the BattleEngine, not stored here.

    Example — "when player struck, reduce attached weapon cooldown by 20%":
        trigger     = ON_PLAYER_STRUCK
        effects     = [ModifierEffect(REDUCE_COOLDOWN, SELF_WEAPON, 0.20)]
        priority    = 10
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str = ""
    icon: str = None
    trigger: EventTrigger
    priority: int = 0                          # Higher = processed first
    effects: list[ModifierEffect] = Field(default_factory=list)
    condition: ModifierCondition | None = None

    # --- Stateful fields ---
    counter: int = 0                           # General-purpose counter
    custom_state: dict[str, Any] = Field(default_factory=dict)
    cooldown_ticks_current: int = 0           # Modifier's own cooldown (ticks elapsed since last trigger)
    cooldown_ticks_max: int = 0               # 0 = no cooldown


# ---------------------------------------------------------------------------
# Weapon
# ---------------------------------------------------------------------------

class Weapon(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    icon: str = None
    base_damage: float
    cooldown_ticks_max: int         # Ticks between fires
    cooldown_ticks_current: int = 0
    modifiers: list[Modifier] = Field(default_factory=list, max_length=3)
    statuses: list[str] = Field(default_factory=list)
    custom_state: dict[str, Any] = Field(default_factory=dict)  # Shared blackboard for modifiers

    @property
    def is_ready(self) -> bool:
        return self.cooldown_ticks_current >= self.cooldown_ticks_max


# ---------------------------------------------------------------------------
# Team
# ---------------------------------------------------------------------------

class Team(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    hp: float
    max_hp: float
    weapons: list[Weapon] = Field(default_factory=list, max_length=3)
    statuses: list[str] = Field(default_factory=list)

    @property
    def is_alive(self) -> bool:
        return self.hp > 0


# ---------------------------------------------------------------------------
# Battle State — the full serializable snapshot
# ---------------------------------------------------------------------------

class BattleState(BaseModel):
    battle_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tick: int = 0
    team_a: Team
    team_b: Team
    is_over: bool = False
    winner_id: str | None = None
    max_cycles_guard: int = 100   # Max event chain depth per tick (anti-loop)
    rng_seed: int = 0             # Seed advanced each time RNG is consumed — keeps client/server in sync