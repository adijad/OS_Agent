class ControlManager:
    def find(
        self,
        window,
        *,
        control_type: str | None = None,
        name: str | None = None,
        automation_id: str | None = None,
    ):
        filters = {}

        if control_type:
            filters["control_type"] = control_type

        if name:
            filters["title"] = name

        if automation_id:
            filters["auto_id"] = automation_id

        controls = window.descendants(**filters)

        if not controls:
            raise RuntimeError(
                f"No matching control found: {filters}"
            )

        return controls[0]

    def focus(self, control):
        control.set_focus()

    def read_text(self, control) -> str:
        text_pattern = control.iface_text
        document_range = text_pattern.DocumentRange

        return document_range.GetText(-1)