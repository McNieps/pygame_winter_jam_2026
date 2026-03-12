from isec.instance.base_instance import BaseInstance
from isec.environment import EntityScene

from game.entities.combat.combat_background import CombatBackground
from game.entities.combat.back_snow_layer import BackSnowLayer
from game.entities.combat.front_snow_layer import FrontSnowLayer
from game.entities.combat.iron_bar import IronBar
from game.entities.combat.combat_floor import CombatFloor
from game.entities.combat.health_bar import HealthBar

from game.battle_engine.models import Team
from game.battle_engine.events import BattleEvent
from game.battle_engine.engine import BattleState, BattleEngine

from game.scenes.combat_sign import CombatSign


class CombatInstance(BaseInstance):
    TICK_PERIOD = 0.1  # s

    def __init__(self,
                 player_team: Team,
                 enemy_team: Team) -> None:

        self.time_since_last_tick = -2
        self.tick = 0
        super().__init__(120)
        self.battle_engine = BattleEngine()
        self.battle_state = BattleState(team_a=player_team, team_b=enemy_team)

        self.iron_bar = IronBar()
        self.background_scene = EntityScene(120, entities=[CombatBackground(), BackSnowLayer(), self.iron_bar, CombatFloor()])
        self.left_health_bar = HealthBar("left", player_team)
        self.right_health_bar = HealthBar("right", enemy_team)
        self.left_combat_sign_scene = CombatSign("left", player_team.weapons)
        self.right_combat_sign_scene = CombatSign("right", enemy_team.weapons)

        self.foreground_scene = EntityScene(120, entities=[FrontSnowLayer(),
                                                               self.left_health_bar,
                                                               self.right_health_bar])

        self.teams = {player_team.id: player_team,
                      enemy_team.id: enemy_team}

        self.team_health = {player_team.id: self.left_health_bar,
                            enemy_team.id: self.right_health_bar}

        self.team_sign = {player_team.id: self.left_combat_sign_scene,
                          enemy_team.id: self.right_combat_sign_scene}

        self.cancel_first_loop = True

    async def loop(self):
        if self.cancel_first_loop:
            self.cancel_first_loop = False
            return

        self.time_since_last_tick += self.delta
        if self.time_since_last_tick > self.TICK_PERIOD:
            self.time_since_last_tick -= self.TICK_PERIOD
            self.battle_state, tick_events = self.battle_engine.tick(self.battle_state)
            self.handle_tick_events(tick_events)

        self.background_scene.update(self.delta)
        self.foreground_scene.update(self.delta)
        self.left_combat_sign_scene.update(self.delta)
        self.right_combat_sign_scene.update(self.delta)

        self.background_scene.render()
        self.left_combat_sign_scene.render()
        self.right_combat_sign_scene.render()
        self.window.blit(self.left_combat_sign_scene.surface, (0, 25))
        self.window.blit(self.right_combat_sign_scene.surface, (200, 25))
        self.foreground_scene.render()

    def handle_tick_events(self, events: list[BattleEvent]):
        self.tick += 1

        for event in events:
            if event.type == "damage_done":
                team_health_bar = self.team_health[event.target_team_id]
                team_health_bar.update_health(event.target_hp_after)
                self.team_sign[event.target_team_id].shake_sign(event.final_damage/team_health_bar.max_health)

            elif event.type == "tick_advanced":
                self.iron_bar.set_snow_progression(self.tick/100)

            elif event.type == "weapon_fired":
                self.team_sign[event.team_id].display_weapon_activation(event.weapon_id)

            elif event.type == "modifier_triggered":
                print("i")
                for sign in self.team_sign.values():
                    if event.modifier_id in sign.modifiers:
                        sign.modifiers[event.modifier_id].display_activation()
                        break

            elif event.type == "effect_applied":
                print("i")
                continue

            elif event.type == "cooldown_changed":
                for sign in self.team_sign.values():
                    if event.weapon_id in sign.weapons:
                        sign.weapons[event.weapon_id].cooldown_remaining = event.new_value

            else:
                print(event)