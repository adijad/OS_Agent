from enum import Enum


class RunStatus(str, Enum):
    CREATED = "created"
    RUNNING = "running"

    COMPLETED = "completed"
    FAILED = "failed"
    STUCK = "stuck"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"
    MAX_STEPS_REACHED = "max_steps_reached"


class StepStatus(str, Enum):
    CREATED = "created"
    RUNNING = "running"

    COMPLETED = "completed"
    FAILED = "failed"


class EventType(str, Enum):
    # =============================================
    # RUN LIFECYCLE
    # =============================================

    RUN_CREATED = "run_created"
    RUN_STARTED = "run_started"

    RUN_COMPLETED = "run_completed"
    RUN_FAILED = "run_failed"
    RUN_STUCK = "run_stuck"
    RUN_MAX_STEPS_REACHED = (
        "run_max_steps_reached"
    )

    # =============================================
    # STEP LIFECYCLE
    # =============================================

    STEP_STARTED = "step_started"

    STEP_COMPLETED = "step_completed"
    STEP_FAILED = "step_failed"

    # =============================================
    # OBSERVATION / REASONING
    # =============================================

    OBSERVATION_CAPTURED = (
        "observation_captured"
    )

    MODEL_REQUESTED = "model_requested"

    ACTION_PROPOSED = "action_proposed"

    # =============================================
    # POLICY
    # =============================================

    POLICY_ALLOWED = "policy_allowed"

    # =============================================
    # EXECUTION
    # =============================================

    ACTION_STARTED = "action_started"

    ACTION_COMPLETED = "action_completed"

    ACTION_FAILED = "action_failed"