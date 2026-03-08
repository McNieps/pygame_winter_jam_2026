import pygame
import typing


class EventHandler:
    def __init__(self,
                 key_dict: dict) -> None:

        self.events = []
        self.mouse_pos = pygame.mouse.get_pos()
        self.mouse_rel = pygame.math.Vector2()
        self._callbacks = self._create_callbacks_dict(key_dict)
        self._keyboard_cbs = {}
        self._mouse_cbs = {}
        self._quit_callbacks = []
        self.sort_callbacks()

    def register_callback(self,
                          action: str,
                          action_type: typing.Literal["up", "down", "pressed"],
                          callback: typing.Callable) -> None:

        if action not in self._callbacks:
            valid_actions = "- "+"\n- ".join(self._callbacks.keys())
            err_msg = f"{action} is not a valid action. Valid actions are: \n{valid_actions}"
            raise ValueError(err_msg)

        if action_type not in ["up", "down", "pressed"]:
            err_msg = f"{action_type} is not a valid action_type. Must be either up, down or pressed."
            raise ValueError(err_msg)

        self._callbacks[action]["callbacks"][action_type].add(callback)
        self.sort_callbacks()


    def register_quit_callback(self,
                               callback: typing.Callable) -> None:

        self._quit_callbacks.append(callback)

    def sort_callbacks(self) -> None:
        self._keyboard_cbs = {}
        self._mouse_cbs = {}

        for action in self._callbacks:
            if self._callbacks[action]["method"] == "keyboard":
                self._keyboard_cbs[action] = self._callbacks[action]
                continue

            if self._callbacks[action]["method"] == "mouse":
                self._mouse_cbs[action] = self._callbacks[action]
                continue

    async def handle_all(self) -> None:
        await self.handle_events()
        await self.handle_pressed()

    async def handle_events(self) -> None:
        self.events = pygame.event.get()
        new_mouse_pos = pygame.math.Vector2(pygame.mouse.get_pos())
        self.mouse_rel = new_mouse_pos - self.mouse_pos
        self.mouse_pos = new_mouse_pos

        for event in self.events:
            if event.type == pygame.QUIT:
                for callback in self._quit_callbacks:
                    await callback()
                continue

            if event.type == pygame.KEYDOWN:
                await self._handle_keyboard("down", event.key)
                continue

            if event.type == pygame.KEYUP:
                await self._handle_keyboard("up", event.key)
                continue

            if event.type == pygame.MOUSEBUTTONDOWN:
                await self._handle_mouse("down", event.button)
                continue

            if event.type == pygame.MOUSEBUTTONUP:
                await self._handle_mouse("up", event.button)
                continue

    async def handle_pressed(self):
        key_pressed = pygame.key.get_pressed()
        for action in self._keyboard_cbs:
            if not key_pressed[self._keyboard_cbs[action]["key"]]:
                continue
            for callback in self._keyboard_cbs[action]["callbacks"]["pressed"]:
                await callback()

        button_pressed = pygame.mouse.get_pressed(5)
        for action in self._mouse_cbs:
            if not button_pressed[self._mouse_cbs[action]["key"]-1]:
                continue
            for callback in self._mouse_cbs[action]["callbacks"]["pressed"]:
                await callback()

    async def _handle_keyboard(self,
                               action_type: typing.Literal["up", "down", "pressed"],
                               action_key: int) -> None:

        for action in self._keyboard_cbs:
            if self._keyboard_cbs[action]["key"] != action_key:
                continue
            for callback in self._keyboard_cbs[action]["callbacks"][action_type]:
                await callback()

    async def _handle_mouse(self,
                            action_type: typing.Literal["up", "down", "pressed"],
                            action_button: int):

        for action in self._mouse_cbs:
            if self._mouse_cbs[action]["key"] != action_button:
                continue
            for callback in self._mouse_cbs[action]["callbacks"][action_type]:
                await callback()

    @classmethod
    def _create_callbacks_dict(cls,
                               key_dict: dict[str, dict[str, str]]) -> dict:

        callbacks_map = {}
        for action, value in key_dict.items():
            method, key = cls._guess_peripheral_and_id(value["key"])
            callbacks_map[action] = {"key": key, "method": method, "callbacks": {"down": set(),
                                                                                 "up": set(),
                                                                                 "pressed": set()}}
        return callbacks_map

    @classmethod
    def _guess_peripheral_and_id(cls,
                                 key_button_str: str) -> tuple[str, int]:

        first_part, second_part = key_button_str.split("_", 1)

        if first_part == "K":
            return "keyboard", vars(pygame)[key_button_str]

        if first_part == "B":
            return "mouse", int(second_part)

        err_msg = (f"control key {key_button_str} is invalid! "
                   f"It must start with either K for keyboard control or B for mouse control")
        raise ValueError(err_msg)
