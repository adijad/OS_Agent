from dataclasses import dataclass
from enum import Enum
from typing import Any


class PolicyDecision(str, Enum):
    """
    The three possible authorization outcomes
    produced by the OS Agent policy layer.
    """

    ALLOW = "allow"

    APPROVAL_REQUIRED = (
        "approval_required"
    )

    BLOCK = "block"


@dataclass(frozen=True)
class PolicyResult:
    """
    Structured result returned by policy
    evaluation.
    """

    decision: PolicyDecision
    reason: str


@dataclass(frozen=True)
class PolicyContext:
    """
    Semantic context used by the PolicyEngine
    when deciding whether an action may execute.

    goal:
        The user's current goal.

    action:
        The normalized OS Agent action.

    target:
        The grounded semantic target from the
        CURRENT computer observation, if one
        exists.

    state:
        The current observed computer state.
    """

    goal: str

    action: dict[str, Any]

    target: (
        dict[str, Any]
        | None
    )

    state: dict[str, Any]