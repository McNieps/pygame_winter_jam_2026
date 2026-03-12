"""
Battle Engine - Core Logic
Interprets BattleState + Modifier data. Emits BattleEvents.
Stateless between calls — pass in a BattleState, get back (BattleState, list[events]).
"""

from collections import deque
from copy import deepcopy

from .models import (
    BattleState, Team, Weapon, Modifier,
    EventTrigger, EffectType, EffectTarget, ModifierCondition,
)
from .events import (
    AnyBattleEvent, TickAdvanced, WeaponFired, DamageDone,
    TeamDefeated, CooldownChanged, ModifierTriggered, EffectApplied,
    StatusApplied, StatusRemoved, ModifierStateChanged, BattleEnded,
)


# ---------------------------------------------------------------------------
# Internal trigger payload — carries context into modifier resolution
# ---------------------------------------------------------------------------

class TriggerContext:
    def __init__(
        self,
        trigger: EventTrigger,
        source_weapon: Weapon | None = None,
        source_team: Team | None = None,
        target_team: Team | None = None,
        damage: int = 0,
    ):
        self.trigger = trigger
        self.source_weapon = source_weapon
        self.source_team = source_team
        self.target_team = target_team
        self.damage = damage


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

class BattleEngine:
    """
    Pure logic processor. No I/O, no game state stored here.

    Usage:
        engine = BattleEngine()
        state, events = engine.tick(state)
        # Feed events to your GUI
        # Serialize state with state.model_dump_json()
    """

    def tick(self, state: BattleState) -> tuple[BattleState, list[AnyBattleEvent]]:
        """Advance the battle by one tick. Returns the new state and all events."""
        if state.is_over:
            return state, []

        state = deepcopy(state)   # Never mutate the input
        events: list[AnyBattleEvent] = [TickAdvanced(tick=state.tick)]

        # 1. Advance cooldowns and collect weapons ready to fire
        self._advance_cooldowns(state, events)

        # 2. Fire ready weapons
        self._fire_weapons(state, events)

        # 3. Check end condition
        self._check_end(state, events)

        state.tick += 1
        return state, events

    # -----------------------------------------------------------------------
    # Phase 1 — Cooldown tick
    # -----------------------------------------------------------------------

    def _advance_cooldowns(self, state: BattleState, events: list) -> None:
        for team in (state.team_a, state.team_b):
            for weapon in team.weapons:
                old_weapon_cd = weapon.cooldown_ticks_current
                if weapon.cooldown_ticks_current < weapon.cooldown_ticks_max:
                    weapon.cooldown_ticks_current += 1
                    events.append(CooldownChanged(tick=state.tick,
                                                  weapon_id=weapon.id,
                                                  old_value=old_weapon_cd,
                                                  new_value=weapon.cooldown_ticks_current))

                # Tick modifier cooldowns
                for mod in weapon.modifiers:
                    if mod.cooldown_ticks_current > mod.cooldown_ticks_max:
                        old = mod.cooldown_ticks_current
                        mod.cooldown_ticks_current += 1
                        events.append(ModifierStateChanged(
                            tick=state.tick,
                            modifier_id=mod.id,
                            modifier_name=mod.name,
                            weapon_id=weapon.id,
                            attribute="cooldown_ticks_current",
                            old_value=old,
                            new_value=mod.cooldown_ticks_current,
                        ))

        # ON_TICK trigger
        ctx = TriggerContext(trigger=EventTrigger.ON_TICK)
        self._dispatch_trigger(state, ctx, events)

    # -----------------------------------------------------------------------
    # Phase 2 — Fire weapons
    # -----------------------------------------------------------------------

    def _fire_weapons(self, state: BattleState, events: list) -> None:
        pairs = [
            (state.team_a, state.team_b),
            (state.team_b, state.team_a),
        ]
        for attacker, defender in pairs:
            for weapon in attacker.weapons:
                if not weapon.is_ready:
                    continue
                if not attacker.is_alive or not defender.is_alive:
                    break

                # Reset cooldown
                weapon.cooldown_ticks_current = 0
                events.append(CooldownChanged(
                    tick=state.tick,
                    weapon_id=weapon.id,
                    old_value=weapon.cooldown_ticks_current,
                    new_value=0,
                ))

                events.append(WeaponFired(
                    tick=state.tick,
                    weapon_id=weapon.id,
                    weapon_name=weapon.name,
                    team_id=attacker.id,
                    source_weapon_id=weapon.id,
                    source_team_id=attacker.id,
                ))

                # ON_WEAPON_FIRE trigger
                ctx_fire = TriggerContext(
                    trigger=EventTrigger.ON_WEAPON_FIRE,
                    source_weapon=weapon,
                    source_team=attacker,
                    target_team=defender,
                )
                self._dispatch_trigger(state, ctx_fire, events)

                # Compute and apply damage
                damage = weapon.base_damage
                self._apply_damage(state, weapon, attacker, defender, damage, events)

                # Reset cooldown
                weapon.cooldown_ticks_current = 0

    def _apply_damage(
        self,
        state: BattleState,
        weapon: Weapon,
        attacker: Team,
        defender: Team,
        damage: int,
        events: list,
    ) -> None:

        hp_before = defender.hp
        defender.hp = max(0, defender.hp - damage)

        events.append(DamageDone(
            tick=state.tick,
            source_weapon_id=weapon.id,
            source_team_id=attacker.id,
            target_team_id=defender.id,
            raw_damage=damage,
            final_damage=damage,
            target_hp_before=hp_before,
            target_hp_after=defender.hp,
        ))

        # ON_DAMAGE_DEALT (attacker side)
        self._dispatch_trigger(state, TriggerContext(
            trigger=EventTrigger.ON_DAMAGE_DEALT,
            source_weapon=weapon, source_team=attacker, target_team=defender, damage=damage,
        ), events)

        # ON_DAMAGE_TAKEN + ON_PLAYER_STRUCK (defender side)
        self._dispatch_trigger(state, TriggerContext(
            trigger=EventTrigger.ON_DAMAGE_TAKEN,
            source_team=defender, target_team=attacker, damage=damage,
        ), events)
        self._dispatch_trigger(state, TriggerContext(
            trigger=EventTrigger.ON_PLAYER_STRUCK,
            source_team=defender, target_team=attacker, damage=damage,
        ), events)

        if not defender.is_alive:
            events.append(TeamDefeated(
                tick=state.tick,
                team_id=defender.id,
                team_name=defender.name,
            ))

    @staticmethod
    def _check_end(state: BattleState, events: list) -> None:
        a_alive = state.team_a.is_alive
        b_alive = state.team_b.is_alive

        if not a_alive or not b_alive:
            state.is_over = True
            if a_alive and not b_alive:
                state.winner_id = state.team_a.id
            elif b_alive and not a_alive:
                state.winner_id = state.team_b.id

            events.append(BattleEnded(tick=state.tick, winner_id=state.winner_id))

    def _dispatch_trigger(self,
                          state: BattleState,
                          initial_ctx: TriggerContext,
                          events: list) -> None:

        queue: deque[TriggerContext] = deque([initial_ctx])
        cycle_count = 0

        while queue:
            if cycle_count >= state.max_cycles_guard:
                # Anti-infinite-loop guard
                break

            ctx = queue.popleft()
            new_contexts = self._resolve_trigger(state, ctx, events)
            queue.extend(new_contexts)
            cycle_count += 1

    def _resolve_trigger(
        self,
        state: BattleState,
        ctx: TriggerContext,
        events: list,
    ) -> list[TriggerContext]:
        """
        Find all modifiers listening to this trigger, sorted by priority (desc).
        Apply their effects and return any new TriggerContexts they produce.
        """
        new_contexts: list[TriggerContext] = []

        # Collect (modifier, weapon, team) triples, across both teams
        candidates: list[tuple[Modifier, Weapon, Team]] = []
        for team in (state.team_a, state.team_b):
            for weapon in team.weapons:
                for mod in weapon.modifiers:
                    if mod.trigger == ctx.trigger:
                        candidates.append((mod, weapon, team))

        # Sort by priority descending
        candidates.sort(key=lambda t: t[0].priority, reverse=True)

        for mod, weapon, team in candidates:
            if not self._check_condition(mod, weapon, team, ctx):
                continue
            if mod.cooldown_ticks_current < mod.cooldown_ticks_max:
                continue  # Modifier on cooldown

            events.append(ModifierTriggered(
                tick=state.tick,
                modifier_id=mod.id,
                modifier_name=mod.name,
                weapon_id=weapon.id,
                trigger=ctx.trigger.value,
                source_weapon_id=weapon.id,
                source_team_id=team.id,
            ))

            downstream = self._apply_modifier_effects(
                state, mod, weapon, team, ctx, events
            )
            new_contexts.extend(downstream)

            # Start modifier cooldown if configured
            if mod.cooldown_ticks_max > 0:
                old = mod.cooldown_ticks_current
                mod.cooldown_ticks_current = 0
                events.append(ModifierStateChanged(
                    tick=state.tick,
                    modifier_id=mod.id,
                    modifier_name=mod.name,
                    weapon_id=weapon.id,
                    attribute="cooldown_ticks_current",
                    old_value=old,
                    new_value=mod.cooldown_ticks_current,
                ))

        return new_contexts

    # -----------------------------------------------------------------------
    # Effect application
    # -----------------------------------------------------------------------

    def _apply_modifier_effects(
        self,
        state: BattleState,
        mod: Modifier,
        weapon: Weapon,
        team: Team,
        ctx: TriggerContext,
        events: list,
    ) -> list[TriggerContext]:
        """Apply all effects of a modifier. Returns any new trigger contexts."""
        new_contexts: list[TriggerContext] = []

        for effect in mod.effects:
            targets = self._resolve_targets(state, effect.target, weapon, team, ctx)

            for target in targets:
                if isinstance(target, Weapon):
                    self._apply_weapon_effect(state, mod, effect, target, events, new_contexts)
                elif isinstance(target, Team):
                    self._apply_team_effect(state, mod, effect, target, events)

        return new_contexts

    def _apply_weapon_effect(self, state, mod, effect, weapon: Weapon, events, new_contexts):
        if effect.effect_type == EffectType.REDUCE_COOLDOWN:
            old = weapon.cooldown_ticks_current
            reduction = weapon.cooldown_ticks_max * effect.value
            weapon.cooldown_ticks_current = max(0, weapon.cooldown_ticks_current - int(reduction))
            events.append(CooldownChanged(
                tick=state.tick, weapon_id=weapon.id,
                old_value=old, new_value=weapon.cooldown_ticks_current,
                cause=mod.name, source_weapon_id=weapon.id,
            ))

        elif effect.effect_type == EffectType.SET_COOLDOWN:
            old = weapon.cooldown_ticks_current
            weapon.cooldown_ticks_current = int(effect.value)
            events.append(CooldownChanged(
                tick=state.tick, weapon_id=weapon.id,
                old_value=old, new_value=weapon.cooldown_ticks_current,
                cause=mod.name, source_weapon_id=weapon.id,
            ))

        elif effect.effect_type == EffectType.APPLY_STATUS:
            if effect.value_str not in weapon.statuses:
                weapon.statuses.append(effect.value_str)
                events.append(StatusApplied(
                    tick=state.tick, target_id=weapon.id,
                    target_type="weapon", status_name=effect.value_str,
                ))

        elif effect.effect_type == EffectType.REMOVE_STATUS:
            if effect.value_str in weapon.statuses:
                weapon.statuses.remove(effect.value_str)
                events.append(StatusRemoved(
                    tick=state.tick, target_id=weapon.id,
                    target_type="weapon", status_name=effect.value_str,
                ))

        elif effect.effect_type == EffectType.INCREMENT_COUNTER:
            old = mod.counter
            mod.counter += 1
            events.append(ModifierStateChanged(
                tick=state.tick, modifier_id=mod.id, modifier_name=mod.name,
                weapon_id=weapon.id, attribute="counter",
                old_value=old, new_value=mod.counter,
            ))
            # Emit a modifier_state trigger so other modifiers can react
            new_contexts.append(TriggerContext(
                trigger=EventTrigger.ON_MODIFIER_STATE,
                source_weapon=weapon,
            ))

        elif effect.effect_type == EffectType.RESET_COUNTER:
            old = mod.counter
            mod.counter = 0
            events.append(ModifierStateChanged(
                tick=state.tick, modifier_id=mod.id, modifier_name=mod.name,
                weapon_id=weapon.id, attribute="counter",
                old_value=old, new_value=0,
            ))

        events.append(EffectApplied(
            tick=state.tick, modifier_id=mod.id, modifier_name=mod.name,
            effect_type=effect.effect_type.value, target_id=weapon.id,
            value=effect.value, value_str=effect.value_str,
        ))

    def _apply_team_effect(self, state, mod, effect, team: Team, events):
        if effect.effect_type == EffectType.HEAL:
            team.hp = min(team.max_hp, team.hp + effect.value)

        elif effect.effect_type == EffectType.APPLY_STATUS:
            if effect.value_str not in team.statuses:
                team.statuses.append(effect.value_str)
                events.append(StatusApplied(
                    tick=state.tick, target_id=team.id,
                    target_type="team", status_name=effect.value_str,
                ))

        elif effect.effect_type == EffectType.REMOVE_STATUS:
            if effect.value_str in team.statuses:
                team.statuses.remove(effect.value_str)
                events.append(StatusRemoved(
                    tick=state.tick, target_id=team.id,
                    target_type="team", status_name=effect.value_str,
                ))

        events.append(EffectApplied(
            tick=state.tick, modifier_id=mod.id, modifier_name=mod.name,
            effect_type=effect.effect_type.value, target_id=team.id,
            value=effect.value, value_str=effect.value_str,
        ))

    # -----------------------------------------------------------------------
    # Target resolution
    # -----------------------------------------------------------------------

    def _resolve_targets(
        self,
        state: BattleState,
        target_type: EffectTarget,
        weapon: Weapon,
        team: Team,
        ctx: TriggerContext,
    ) -> list[Weapon | Team]:
        if target_type == EffectTarget.SELF_WEAPON:
            return [weapon]

        elif target_type == EffectTarget.ALL_ALLY_WEAPONS:
            return list(team.weapons)

        elif target_type == EffectTarget.ENEMY_TEAM:
            return [state.team_b if team.id == state.team_a.id else state.team_a]

        elif target_type == EffectTarget.TRIGGERING_WEAPON:
            return [ctx.source_weapon] if ctx.source_weapon else []

        return []

    # -----------------------------------------------------------------------
    # Condition check
    # -----------------------------------------------------------------------

    def _check_condition(
        self,
        mod: Modifier,
        weapon: Weapon,
        team: Team,
        ctx: TriggerContext,
    ) -> bool:
        if mod.condition is None:
            return True

        c = mod.condition
        attr_map = {
            "counter": mod.counter,
            "hp_pct": team.hp / team.max_hp if team.max_hp > 0 else 0,
            "cooldown_current": weapon.cooldown_ticks_current,
        }

        actual = attr_map.get(c.attribute)
        if actual is None:
            # Fall back to modifier custom_state
            actual = mod.custom_state.get(c.attribute)
        if actual is None:
            return False

        ops = {
            ">=": actual >= c.value,
            "<=": actual <= c.value,
            "==": actual == c.value,
            ">":  actual > c.value,
            "<":  actual < c.value,
        }
        return ops.get(c.operator, False)
