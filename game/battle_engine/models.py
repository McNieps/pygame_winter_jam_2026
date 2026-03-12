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
    ON_WEAPON_HIT     = "on_weapon_hit"
    ON_PLAYER_STRUCK  = "on_player_struck"
    ON_KILL           = "on_kill"
    ON_BATTLE_START   = "on_battle_start"
    ON_MODIFIER_STATE = "on_modifier_state"


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


class EffectTarget(str, Enum):
    """Who/what the effect applies to."""
    SELF_WEAPON     = "self_weapon"       # Weapon this modifier is attached to
    ALL_ALLY_WEAPONS = "all_ally_weapons"
    ENEMY_TEAM      = "enemy_team"
    TRIGGERING_WEAPON = "triggering_weapon"  # The weapon that caused the event


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
    custom_state: dict[str, Any] = Field(default_factory=dict)
    cooldown_ticks_current: int = 0
    cooldown_ticks_max: int = 0


class Weapon(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    icon: str = None
    base_damage: int
    cooldown_ticks_current: int = 0
    cooldown_ticks_max: int         # Ticks between fires
    modifiers: list[Modifier] = Field(default_factory=list, max_length=3)
    statuses: list[str] = Field(default_factory=list)

    @property
    def is_ready(self) -> bool:
        return self.cooldown_ticks_current >= self.cooldown_ticks_max


class Team(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    hp: int
    max_hp: int
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
