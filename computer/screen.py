from pathlib import Path
from uuid import uuid4

import win32gui
from PIL import ImageGrab


class ScreenManager:
    def __init__(
        self,
        output_dir: str = ".runtime/screenshots",
    ):
        self.output_dir = Path(output_dir)

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def capture_active_window(self):
        """
        Capture the actual visible pixels occupied by the
        currently focused Windows window.
        """

        hwnd = win32gui.GetForegroundWindow()

        if not hwnd:
            raise RuntimeError(
                "Could not determine the active window."
            )

        title = win32gui.GetWindowText(hwnd)

        left, top, right, bottom = (
            win32gui.GetWindowRect(hwnd)
        )

        if right <= left or bottom <= top:
            raise RuntimeError(
                "Active window has an invalid screen rectangle."
            )

        screenshot = ImageGrab.grab(
            bbox=(
                left,
                top,
                right,
                bottom,
            ),
            all_screens=True,
        )

        screenshot_id = uuid4().hex[:8]

        path = (
            self.output_dir
            / f"{screenshot_id}.png"
        )

        screenshot.save(path)

        return {
            "id": screenshot_id,
            "window_title": title,
            "path": str(path),
            "width": screenshot.width,
            "height": screenshot.height,
            "bounds": {
                "left": left,
                "top": top,
                "right": right,
                "bottom": bottom,
            },
        }