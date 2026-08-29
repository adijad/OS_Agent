from .policy_types import (
    PolicyContext,
    PolicyDecision,
    PolicyResult,
)


class PolicyViolationError(Exception):
    pass


class PolicyEngine:
    """
    System-owned authorization layer for
    OS Agent actions.

    Policy evaluation produces an explicit
    PolicyResult instead of directly executing
    or approving an action.

    The legacy check() method remains temporarily
    for compatibility with the current AgentLoop.
    """

    # =============================================
    # POLICY V1 EVALUATION API
    # =============================================

    def evaluate(
        self,
        *,
        context: PolicyContext,
    ) -> PolicyResult:
        """
        Evaluate a semantic OS Agent action.

        Policy decisions are explicit:

            ALLOW
            APPROVAL_REQUIRED
            BLOCK

        Policy v1 currently preserves the
        autonomous behavior of the existing
        policy implementation.

        Consequential semantic rules will be
        introduced after this API is wired into
        AgentLoop.
        """

        action = context.action

        action_type = action.get(
            "action"
        )

        # -----------------------------------------
        # MALFORMED ACTION
        # -----------------------------------------

        if not action_type:
            return PolicyResult(
                decision=PolicyDecision.BLOCK,
                reason=(
                    "Action does not specify "
                    "an action type."
                ),
            )

        # -----------------------------------------
        # OPEN APPLICATION
        #
        # Existing behavior:
        # application launch is permitted.
        # -----------------------------------------

        if (
            action_type
            == "open_application"
        ):
            return PolicyResult(
                decision=PolicyDecision.ALLOW,
                reason=(
                    "Opening an application is "
                    "currently permitted."
                ),
            )

        # -----------------------------------------
        # FOCUS WINDOW
        #
        # Window focus must remain grounded in
        # the CURRENT observation.
        # -----------------------------------------

        if (
            action_type
            == "focus_window"
        ):
            target = context.target

            if (
                target is not None
                and target.get("role")
                == "Window"
            ):
                return PolicyResult(
                    decision=PolicyDecision.ALLOW,
                    reason=(
                        "Focus target is grounded "
                        "in the current observation."
                    ),
                )

            return PolicyResult(
                decision=PolicyDecision.BLOCK,
                reason=(
                    "Requested focus target was "
                    "not found as a window in the "
                    "current observation."
                ),
            )

        # -----------------------------------------
        # CURRENT DEFAULT
        #
        # Preserve existing autonomous behavior
        # until semantic risk rules are added.
        # -----------------------------------------

        return PolicyResult(
            decision=PolicyDecision.ALLOW,
            reason=(
                "Action is permitted by the "
                "current default policy."
            ),
        )

    # =============================================
    # LEGACY COMPATIBILITY API
    #
    # AgentLoop still calls check(action, state).
    #
    # We leave this path unchanged until the next
    # integration phase so the existing agent
    # behavior remains stable.
    # =============================================

    def check(
        self,
        *,
        action: dict,
        state: dict,
    ):
        """
        Temporary compatibility path for the
        current AgentLoop.

        This method will be removed once
        AgentLoop consumes PolicyResult directly.
        """

        action_type = action[
            "action"
        ]

        semantic = state[
            "semantic"
        ]

        if (
            action_type
            == "open_application"
        ):
            return True

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

        return True