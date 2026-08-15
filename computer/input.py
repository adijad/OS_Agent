from time import sleep

import win32api
from pywinauto import mouse
from pywinauto.keyboard import send_keys


class InputManager:
    def type_text(
        self,
        control,
        text: str,
        *,
        clear_first: bool = False,
    ):
        control.set_focus()

        sleep(0.2)

        if clear_first:
            send_keys("^a")
            send_keys("{BACKSPACE}")

        send_keys(
            text,
            with_spaces=True,
            pause=0.03,
        )

    def press(self, keys: str):
        send_keys(keys)

    def click(
        self,
        control,
        *,
        duration: float = 0.35,
        steps: int = 20,
    ):
        """
        Physically move the mouse to the center of a UI control
        and click it.
        """

        rectangle = control.rectangle()

        if rectangle.width() <= 0 or rectangle.height() <= 0:
            raise RuntimeError(
                "Cannot click a control with an invalid rectangle."
            )

        target_x = (
            rectangle.left + rectangle.right
        ) // 2

        target_y = (
            rectangle.top + rectangle.bottom
        ) // 2

        self._move_mouse_smoothly(
            target_x,
            target_y,
            duration=duration,
            steps=steps,
        )

        mouse.click(
            button="left",
            coords=(target_x, target_y),
        )

    def _move_mouse_smoothly(
        self,
        target_x: int,
        target_y: int,
        *,
        duration: float,
        steps: int,
    ):
        start_x, start_y = win32api.GetCursorPos()

        for step in range(1, steps + 1):
            progress = step / steps

            current_x = int(
                start_x
                + (target_x - start_x) * progress
            )

            current_y = int(
                start_y
                + (target_y - start_y) * progress
            )

            mouse.move(
                coords=(current_x, current_y)
            )

            sleep(duration / steps)