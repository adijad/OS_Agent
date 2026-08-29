from dataclasses import dataclass
from enum import Enum


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

    decision:
        Whether execution is allowed,
        requires human approval, or is blocked.

    reason:
        Human-readable explanation for why
        the decision was made.
    """

    decision: PolicyDecision
    reason: str