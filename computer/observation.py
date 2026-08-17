from uuid import uuid4

import win32gui
from pywinauto import Desktop


INTERACTIVE_CONTROL_TYPES = {
    "Button",
    "MenuItem",
    "Edit",
    "Document",
    "ListItem",
    "TabItem",
    "CheckBox",
    "RadioButton",
    "ComboBox",
    "SplitButton",
    "Hyperlink",
    "TreeItem",
}


IGNORED_EMPTY_CONTROL_TYPES = {
    "Pane",
    "Group",
    "Custom",
    "Image",
    "TitleBar",
    "Tab",
    "List",
    "MenuBar",
}


IGNORED_WINDOW_CLASSES = {
    "Shell_TrayWnd",  # Taskbar
    "Progman",        # Program Manager / desktop shell
}


class ObservationManager:
    def __init__(self):
        self.desktop = Desktop(backend="uia")

        # Maps temporary IDs to real pywinauto objects.
        self._targets = {}

        self._snapshot_id = None

    def observe(
        self,
        max_controls: int = 80,
        max_text_chars: int = 500,
    ):
        # Every observation gets a new ID.
        self._snapshot_id = uuid4().hex[:8]

        # Old target references become invalid.
        self._targets = {}

        foreground_handle = win32gui.GetForegroundWindow()

        windows = []
        active_window = None
        active_wrapper = None

        window_index = 0

        # -------------------------
        # DESKTOP-LEVEL OBSERVATION
        # -------------------------

        for window in self.desktop.windows():
            try:
                title = window.window_text().strip()
                class_name = window.element_info.class_name

                if not title:
                    continue

                if not window.is_visible():
                    continue

                if class_name in IGNORED_WINDOW_CLASSES:
                    continue

                window_index += 1

                target_id = (
                    f"{self._snapshot_id}:window:{window_index}"
                )

                self._targets[target_id] = window

                window_data = {
                    "id": target_id,
                    "title": title,
                }

                windows.append(window_data)

                if window.handle == foreground_handle:
                    active_window = window_data
                    active_wrapper = window

            except Exception:
                continue

        # -------------------------
        # ACTIVE-WINDOW CONTROLS
        # -------------------------

        controls = []

        if active_wrapper is not None:
            control_index = 0

            for control in active_wrapper.descendants():
                try:
                    if not self._should_include_control(control):
                        continue

                    control_index += 1

                    target_id = (
                        f"{self._snapshot_id}:control:{control_index}"
                    )

                    self._targets[target_id] = control

                    info = control.element_info

                    control_type = info.control_type
                    name = (info.name or "").strip()

                    control_data = {
                        "id": target_id,
                        "role": control_type,
                        "name": name,
                        "interactive": (
                            control_type
                            in INTERACTIVE_CONTROL_TYPES
                        ),
                    }

                    text = self._try_read_text(
                        control,
                        max_chars=max_text_chars,
                    )

                    if text:
                        control_data["text"] = text

                    value = self._try_read_value(
                        control,
                        max_chars=max_text_chars,
                    )

                    if value:
                        control_data["value"] = value

                    controls.append(control_data)

                    # IMPORTANT:
                    # Limit meaningful controls, not raw UIA nodes.
                    if len(controls) >= max_controls:
                        break

                except Exception:
                    continue

        return {
            "snapshot_id": self._snapshot_id,
            "active_window": active_window,
            "windows": windows,
            "controls": controls,
        }

    def resolve(self, target_id: str):
        """
        Convert an agent-facing temporary target ID
        back into the actual pywinauto object.
        """

        target = self._targets.get(target_id)

        if target is None:
            raise RuntimeError(
                f"Unknown or stale target reference: {target_id}"
            )

        return target

    def _should_include_control(self, control) -> bool:
        try:
            if not control.is_visible():
                return False
            info = control.element_info

            name = (info.name or "").strip()
            control_type = info.control_type

            if (
                not name
                and control_type in IGNORED_EMPTY_CONTROL_TYPES
            ):
                return False


            if (
                name == "System"
                and control_type in {"MenuBar", "MenuItem"}
            ):
                return False

            return True

        except Exception:
            return False

    def _try_read_text(
        self,
        control,
        max_chars: int = 500,
    ):
        """
        Try to retrieve textual content from controls
        that are likely to contain readable text.
        """

        control_type = control.element_info.control_type

        if control_type not in {
            "Document",
            "Edit",
            "Text",
        }:
            return None

        try:
            text_pattern = control.iface_text
            document_range = text_pattern.DocumentRange

            text = document_range.GetText(max_chars)

            text = text.strip()

            return text or None

        except Exception:
            return None

    def _try_read_value(
        self,
        control,
        max_chars: int = 500,
    ):
        """
        Try to retrieve a control's current UIA value.

        This is especially useful for single-line Edit
        controls such as browser address bars, search
        fields, file-name inputs, and similar controls.
        """

        try:
            value_pattern = control.iface_value

            value = (
                value_pattern
                .CurrentValue
            )

            if value is None:
                return None

            value = str(value).strip()

            if not value:
                return None

            return value[:max_chars]

        except Exception:
            return None