from time import sleep

import win32api
from pywinauto import mouse
from pywinauto.keyboard import send_keys


SPECIAL_KEY_TOKENS = {
    "ENTER": "{ENTER}",
    "ESC": "{ESC}",
    "TAB": "{TAB}",
    "BACKSPACE": "{BACKSPACE}",
    "DELETE": "{DELETE}",
    "SPACE": "{SPACE}",
    "LEFT": "{LEFT}",
    "RIGHT": "{RIGHT}",
    "UP": "{UP}",
    "DOWN": "{DOWN}",
    "HOME": "{HOME}",
    "END": "{END}",
    "PAGEUP": "{PGUP}",
    "PAGEDOWN": "{PGDN}",
    "INSERT": "{INSERT}",
    "F1": "{F1}",
    "F2": "{F2}",
    "F3": "{F3}",
    "F4": "{F4}",
    "F5": "{F5}",
    "F6": "{F6}",
    "F7": "{F7}",
    "F8": "{F8}",
    "F9": "{F9}",
    "F10": "{F10}",
    "F11": "{F11}",
    "F12": "{F12}",
}


MODIFIER_TOKENS = {
    "CTRL": "^",
    "ALT": "%",
    "SHIFT": "+",
}


LITERAL_ESCAPE_MAP = {
    "{": "{{}",
    "}": "{}}",
    "+": "{+}",
    "^": "{^}",
    "%": "{%}",
    "~": "{~}",
    "(": "{(}",
    ")": "{)}",
}


class InputManager:
    def type_text(
        self,
        control,
        text: str,
        *,
        clear_first: bool = False,
    ):
        """
        Type literal text into the selected control.

        The caller does NOT need to know anything
        about pywinauto's special-key syntax.
        """

        control.set_focus()

        sleep(0.2)

        if clear_first:
            send_keys("^a")
            send_keys(
                "{BACKSPACE}"
            )

        escaped_text = (
            self._escape_literal_text(
                text
            )
        )

        send_keys(
            escaped_text,
            with_spaces=True,
            with_tabs=True,
            with_newlines=True,
            pause=0.03,
        )

    def type_text_global(
        self,
        text: str,
    ):
        """
        Type literal text into whatever control
        currently owns keyboard focus.

        Useful for operating system surfaces such
        as Windows Start/Search.
        """

        escaped_text = (
            self._escape_literal_text(
                text
            )
        )

        send_keys(
            escaped_text,
            with_spaces=True,
            with_tabs=True,
            with_newlines=True,
            pause=0.03,
        )

    def press_key(
        self,
        key: str,
    ):
        """
        Press one semantic special key.

        Example:
            ENTER
            ESC
            TAB
        """

        normalized = key.upper()

        token = (
            SPECIAL_KEY_TOKENS.get(
                normalized
            )
        )

        if token is None:
            raise ValueError(
                f"Unsupported key: "
                f"{key!r}"
            )

        send_keys(
            token
        )

    def hotkey(
        self,
        keys: list[str],
    ):
        """
        Execute a semantic keyboard shortcut.

        Examples:
            ["CTRL", "L"]
            ["CTRL", "SHIFT", "S"]
            ["ALT", "F4"]
            ["WIN", "E"]
        """

        normalized = [
            key.upper()
            for key in keys
        ]

        has_win = (
            "WIN" in normalized
        )

        modifiers = [
            key
            for key in normalized
            if key in {
                "CTRL",
                "ALT",
                "SHIFT",
            }
        ]

        non_modifiers = [
            key
            for key in normalized
            if key not in {
                "CTRL",
                "ALT",
                "SHIFT",
                "WIN",
            }
        ]

        if len(non_modifiers) != 1:
            raise ValueError(
                "Hotkey requires exactly "
                "one non-modifier key."
            )

        final_key = (
            non_modifiers[0]
        )

        modifier_sequence = "".join(
            MODIFIER_TOKENS[key]
            for key in modifiers
        )

        final_token = (
            self._hotkey_key_token(
                final_key
            )
        )

        if has_win:
            sequence = (
                "{VK_LWIN down}"
                + modifier_sequence
                + final_token
                + "{VK_LWIN up}"
            )
        else:
            sequence = (
                modifier_sequence
                + final_token
            )

        send_keys(
            sequence
        )

    def click(
        self,
        control,
        *,
        duration: float = 0.35,
        steps: int = 20,
    ):
        rectangle = (
            control.rectangle()
        )

        if (
            rectangle.width() <= 0
            or rectangle.height() <= 0
        ):
            raise RuntimeError(
                "Cannot click a control "
                "with an invalid rectangle."
            )

        target_x = (
            rectangle.left
            + rectangle.right
        ) // 2

        target_y = (
            rectangle.top
            + rectangle.bottom
        ) // 2

        self._move_mouse_smoothly(
            target_x,
            target_y,
            duration=duration,
            steps=steps,
        )

        mouse.click(
            button="left",
            coords=(
                target_x,
                target_y,
            ),
        )

    def _escape_literal_text(
        self,
        text: str,
    ) -> str:
        return "".join(
            LITERAL_ESCAPE_MAP.get(
                char,
                char,
            )
            for char in text
        )

    def _hotkey_key_token(
        self,
        key: str,
    ) -> str:
        if key in SPECIAL_KEY_TOKENS:
            return (
                SPECIAL_KEY_TOKENS[
                    key
                ]
            )

        if (
            len(key) == 1
            and key.isalnum()
        ):
            # Lowercase avoids accidentally
            # introducing Shift for letters.
            return key.lower()

        raise ValueError(
            f"Unsupported hotkey key: "
            f"{key!r}"
        )

    def _move_mouse_smoothly(
        self,
        target_x: int,
        target_y: int,
        *,
        duration: float,
        steps: int,
    ):
        start_x, start_y = (
            win32api.GetCursorPos()
        )

        for step in range(
            1,
            steps + 1,
        ):
            progress = (
                step / steps
            )

            current_x = int(
                start_x
                + (
                    target_x
                    - start_x
                )
                * progress
            )

            current_y = int(
                start_y
                + (
                    target_y
                    - start_y
                )
                * progress
            )

            mouse.move(
                coords=(
                    current_x,
                    current_y,
                )
            )

            sleep(
                duration / steps
            )