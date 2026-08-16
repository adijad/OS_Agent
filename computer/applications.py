from time import sleep

from pywinauto import Desktop
from pywinauto.application import Application


APPLICATION_TITLE_ALIASES = {
    "calculator": [
        "calculator",
    ],

    "notepad": [
        "notepad",
    ],

    "google chrome": [
        "google chrome",
        "chrome",
    ],

    "chrome": [
        "google chrome",
        "chrome",
    ],

    "visual studio code": [
        "visual studio code",
        "vs code",
    ],

    "vs code": [
        "visual studio code",
        "vs code",
    ],
}


class ApplicationManager:
    def __init__(self):
        self.desktop = Desktop(
            backend="uia"
        )

    # =====================================================
    # EXISTING LOW-LEVEL HELPERS
    # =====================================================

    def find_window(
        self,
        title_pattern: str,
    ):
        window = self.desktop.window(
            title_re=title_pattern
        )

        if window.exists(
            timeout=1
        ):
            return window

        return None

    def launch(
        self,
        executable: str,
    ):
        """
        Low-level executable launch.

        Kept for internal utilities and benchmarks.

        The reasoning model should normally use
        open_application instead.
        """

        Application(
            backend="uia"
        ).start(
            executable
        )

    def ensure(
        self,
        *,
        title_pattern: str,
        executable: str,
        timeout: int = 10,
    ):
        """
        Existing deterministic helper.

        Useful for controlled benchmark setup.
        """

        window = self.find_window(
            title_pattern
        )

        if window is None:
            self.launch(
                executable
            )

            window = (
                self.desktop.window(
                    title_re=title_pattern
                )
            )

            window.wait(
                (
                    "exists visible "
                    "enabled ready"
                ),
                timeout=timeout,
            )

        self._focus_window(
            window
        )

        return window

    # =====================================================
    # GENERAL APPLICATION OPENING
    # =====================================================

    def find_application_window(
        self,
        application: str,
    ):
        """
        Search currently visible top-level windows
        for an application.

        This is deliberately based on observable
        desktop state rather than process assumptions.
        """

        search_names = (
            self._application_aliases(
                application
            )
        )

        for window in (
            self.desktop.windows()
        ):
            try:
                if not window.is_visible():
                    continue

                title = (
                    window
                    .window_text()
                    .strip()
                )

                if not title:
                    continue

                normalized_title = (
                    title.lower()
                )

                for name in search_names:
                    if (
                        name
                        in normalized_title
                    ):
                        return window

            except Exception:
                continue

        return None

    def open_application(
        self,
        application: str,
        *,
        input_manager,
    ):
        """
        Open or focus an application by friendly name.

        Behavior:

        1. If an appropriate visible window already
           exists, focus it instead of launching a
           duplicate.

        2. Otherwise, visibly use Windows Start/Search
           to launch the requested application.

        3. Do not claim the app actually opened.
           AgentLoop will observe the desktop again
           on the next step.
        """

        application = (
            application.strip()
        )

        if not application:
            raise ValueError(
                "Application name "
                "cannot be empty."
            )

        # ---------------------------------------------
        # First check current desktop state.
        # ---------------------------------------------

        existing_window = (
            self.find_application_window(
                application
            )
        )

        if (
            existing_window
            is not None
        ):
            title = (
                existing_window
                .window_text()
                .strip()
            )

            self._focus_window(
                existing_window
            )

            return {
                "status": "success",
                "action":
                    "open_application",
                "application":
                    application,
                "already_open":
                    True,
                "window_title":
                    title,
            }

        # ---------------------------------------------
        # Not currently visible.
        #
        # Open Windows Start using Ctrl+Esc.
        # This is intentionally visible OS interaction.
        # ---------------------------------------------

        input_manager.hotkey(
            [
                "CTRL",
                "ESC",
            ]
        )

        sleep(0.6)

        # Typing while Start is open invokes
        # Windows search.
        input_manager.type_text_global(
            application
        )

        sleep(0.8)

        # Launch the top search result.
        input_manager.press_key(
            "ENTER"
        )

        # Give Windows enough time to begin
        # creating the application window.
        sleep(1.5)

        return {
            "status": "success",
            "action":
                "open_application",
            "application":
                application,
            "already_open":
                False,
        }

    # =====================================================
    # INTERNAL HELPERS
    # =====================================================

    def _application_aliases(
        self,
        application: str,
    ):
        normalized = (
            application
            .strip()
            .lower()
        )

        aliases = (
            APPLICATION_TITLE_ALIASES
            .get(
                normalized
            )
        )

        if aliases:
            return aliases

        # Generic fallback.
        #
        # This lets applications outside our tiny
        # alias table still work when their friendly
        # name appears in their window title.
        return [
            normalized
        ]

    def _focus_window(
        self,
        window,
    ):
        try:
            window.restore()

        except Exception:
            pass

        window.set_focus()