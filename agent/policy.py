class PolicyViolationError(Exception):
    pass


class PolicyEngine:
    def check(
        self,
        *,
        action: dict,
        state: dict,
    ):
        active_window = (
            state["semantic"].get(
                "active_window"
            )
        )

        if not active_window:
            raise PolicyViolationError(
                "No active window was observed."
            )

        title = active_window.get(
            "title",
            ""
        )

        # FIRST AUTONOMOUS TEST ONLY
        if "Calculator" not in title:
            raise PolicyViolationError(
                "Autonomous execution is currently "
                "restricted to Calculator."
            )

        if (
            action["action"]
            == "launch_application"
        ):
            raise PolicyViolationError(
                "Application launching is disabled "
                "during the first autonomous test."
            )

        return True