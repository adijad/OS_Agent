class PolicyViolationError(Exception):
    pass


class PolicyEngine:
    def check(
        self,
        *,
        action: dict,
        state: dict,
    ):
        """
        Basic general-purpose autonomous policy.

        At this stage our available actions are
        low-level computer interaction primitives.

        Consequential semantic actions such as
        purchases, sending messages, deleting files,
        or changing security settings will receive
        stronger approval rules later.
        """

        action_type = action[
            "action"
        ]

        semantic = state[
            "semantic"
        ]

        # ---------------------------------------------
        # Opening an application is currently allowed.
        # ---------------------------------------------

        if (
            action_type
            == "open_application"
        ):
            return True

        # ---------------------------------------------
        # focus_window must refer to a window from
        # the CURRENT observation.
        # ---------------------------------------------

        if (
            action_type
            == "focus_window"
        ):
            target_id = action.get(
                "target"
            )

            for window in semantic.get(
                "windows",
                [],
            ):
                if (
                    window.get("id")
                    == target_id
                ):
                    return True

            raise PolicyViolationError(
                "Requested focus target "
                "was not found in the "
                "current observation."
            )

        # ---------------------------------------------
        # Other actions remain permitted for now.
        #
        # Target validation / stale target rejection
        # still occurs in the executor / observation
        # system.
        # ---------------------------------------------

        return True