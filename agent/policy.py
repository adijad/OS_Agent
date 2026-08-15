class PolicyViolationError(Exception):
    pass


class PolicyEngine:
    def check(
        self,
        *,
        action: dict,
        state: dict,
    ):
        action_type = action["action"]

        semantic = state["semantic"]

        active_window = semantic.get(
            "active_window"
        )

        # Application launching stays disabled
        # during the Calculator benchmark.
        if action_type == "launch_application":
            raise PolicyViolationError(
                "Application launching is disabled "
                "during the Calculator benchmark."
            )

        # Allow recovery when Calculator lost focus.
        if action_type == "focus_window":
            target_id = action.get(
                "target"
            )

            for window in semantic.get(
                "windows",
                [],
            ):
                if window.get("id") != target_id:
                    continue

                title = window.get(
                    "title",
                    "",
                )

                if "Calculator" in title:
                    return True

                raise PolicyViolationError(
                    "The agent may only focus "
                    "Calculator during this benchmark."
                )

            raise PolicyViolationError(
                "Requested focus target "
                "was not found."
            )

        # Normal interactions require Calculator
        # to currently be active.
        if not active_window:
            raise PolicyViolationError(
                "No active window was observed."
            )

        title = active_window.get(
            "title",
            "",
        )

        if "Calculator" not in title:
            raise PolicyViolationError(
                "Autonomous execution is currently "
                "restricted to Calculator."
            )

        return True