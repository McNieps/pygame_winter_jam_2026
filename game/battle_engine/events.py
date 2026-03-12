from typing import Annotated, Literal, Union
from pydantic import BaseModel, Field
import uuid


class BattleEvent(BaseModel):
    """Base class for all battle events."""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tick: int
    source_weapon_id: str | None = None   # Weapon that caused this event
    source_team_id: str | None = None


class WeaponFired(BattleEvent):
    """A weapon completed its cooldown and fired."""
    type: Literal["weapon_fired"] = "weapon_fired"
    weapon_id: str
    weapon_name: str
    team_id: str


class DamageDone(BattleEvent):
    """Damage was applied to a team."""
    type: Literal["damage_done"] = "damage_done"
    target_team_id: str
    raw_damage: int
    final_damage: int     # After modifiers/reductions
    target_hp_before: int
    target_hp_after: int


class TeamDefeated(BattleEvent):
    """A team's HP reached 0."""
    type: Literal["team_defeated"] = "team_defeated"
    team_id: str
    team_name: str


class CooldownChanged(BattleEvent):
    """A weapon's cooldown was modified (e.g. by a modifier effect)."""
    type: Literal["cooldown_changed"] = "cooldown_changed"
    weapon_id: str
    old_value: float
    new_value: float
    cause: str = ""     # Human-readable reason, e.g. modifier name


class ModifierTriggered(BattleEvent):
    """A modifier reacted to an event and produced effects."""
    type: Literal["modifier_triggered"] = "modifier_triggered"
    modifier_id: str
    modifier_name: str
    weapon_id: str      # Weapon the modifier is attached to
    trigger: str        # EventTrigger value


class EffectApplied(BattleEvent):
    """A single modifier effect was applied."""
    type: Literal["effect_applied"] = "effect_applied"
    modifier_id: str
    modifier_name: str
    effect_type: str    # EffectType value
    target_id: str      # Weapon or team ID affected
    value: float = 0.0
    value_str: str = ""


class StatusApplied(BattleEvent):
    """A status was added to a weapon or team."""
    type: Literal["status_applied"] = "status_applied"
    target_id: str
    target_type: str    # "weapon" or "team"
    status_name: str


class StatusRemoved(BattleEvent):
    """A status was removed from a weapon or team."""
    type: Literal["status_removed"] = "status_removed"
    target_id: str
    target_type: str
    status_name: str


class ModifierStateChanged(BattleEvent):
    """A modifier's internal state changed (counter, custom_state, etc.)."""
    type: Literal["modifier_state_changed"] = "modifier_state_changed"
    modifier_id: str
    modifier_name: str
    weapon_id: str
    attribute: str      # "counter", "cooldown_ticks_remaining", etc.
    old_value: float | int | str
    new_value: float | int | str


class TickAdvanced(BattleEvent):
    """Emitted once per tick, before any weapon fires. Useful for GUI sync."""
    type: Literal["tick_advanced"] = "tick_advanced"
    tick: int


class BattleEnded(BattleEvent):
    """The battle is over."""
    type: Literal["battle_ended"] = "battle_ended"
    winner_id: str | None   # None = draw


# ---------------------------------------------------------------------------
# Discriminated union — use this for deserialization and GUI dispatch
# ---------------------------------------------------------------------------

AnyBattleEvent = Annotated[
    Union[
        WeaponFired,
        DamageDone,
        TeamDefeated,
        CooldownChanged,
        ModifierTriggered,
        EffectApplied,
        StatusApplied,
        StatusRemoved,
        ModifierStateChanged,
        TickAdvanced,
        BattleEnded,
    ],
    Field(discriminator="type"),
]
