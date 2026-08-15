from time import sleep

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