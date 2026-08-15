from pywinauto import Desktop
from pywinauto.application import Application


class ApplicationManager:
    def __init__(self):
        self.desktop = Desktop(backend="uia")

    def find_window(self, title_pattern: str):
        window = self.desktop.window(title_re=title_pattern)

        if window.exists(timeout=1):
            return window

        return None

    def launch(self, executable: str):
        Application(backend="uia").start(executable)

    def ensure(
        self,
        *,
        title_pattern: str,
        executable: str,
        timeout: int = 10,
    ):
        window = self.find_window(title_pattern)

        if window is None:
            self.launch(executable)

            window = self.desktop.window(
                title_re=title_pattern
            )

            window.wait(
                "exists visible enabled ready",
                timeout=timeout,
            )

        try:
            window.restore()
        except Exception:
            pass

        window.set_focus()

        return window