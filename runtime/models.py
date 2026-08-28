from dataclasses import (
    dataclass,
    field,
)

from datetime import (
    datetime,
    timezone,
)

from typing import Any

from uuid import uuid4

from .status import (
    EventType,
    RunStatus,
    StepStatus,
)


# =============================================
# HELPERS
# =============================================


def utc_now() -> datetime:
    """
    Return the current UTC time as a
    timezone-aware datetime.
    """

    return datetime.now(
        timezone.utc
    )


def new_id(
    prefix: str,
) -> str:
    """
    Create a globally unique runtime identifier.

    Examples:

    run_f31b...
    step_91ac...
    evt_17cd...
    """

    return (
        f"{prefix}_{uuid4().hex}"
    )


# =============================================
# RUN
# =============================================


@dataclass
class Run:
    """
    Represents one user goal from creation
    through a terminal execution outcome.
    """

    run_id: str

    goal: str

    status: RunStatus

    created_at: datetime

    started_at: (
        datetime | None
    ) = None

    completed_at: (
        datetime | None
    ) = None

    current_step: int = 0

    outcome: (
        str | None
    ) = None


# =============================================
# STEP
# =============================================


@dataclass
class Step:
    """
    Represents one execution step belonging
    to a Run.
    """

    step_id: str

    run_id: str

    number: int

    status: StepStatus

    started_at: datetime

    completed_at: (
        datetime | None
    ) = None

    proposed_action: (
        dict[str, Any] | None
    ) = None

    outcome: (
        str | None
    ) = None


# =============================================
# RUNTIME EVENT
# =============================================


@dataclass
class RuntimeEvent:
    """
    Represents one meaningful semantic event
    in the lifecycle of an execution run.
    """

    event_id: str

    run_id: str

    event_type: EventType

    timestamp: datetime

    step_id: (
        str | None
    ) = None

    data: dict[str, Any] = field(
        default_factory=dict
    )