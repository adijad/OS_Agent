from typing import Any

from .models import (
    Run,
    RuntimeEvent,
    Step,
    new_id,
    utc_now,
)

from .status import (
    EventType,
    RunStatus,
    StepStatus,
)

from .store import (
    SQLiteRunStore,
)


class ExecutionRuntime:
    """
    Coordinates the semantic lifecycle of
    OS Agent execution.

    The runtime owns state transitions.

    The store owns persistence.
    """

    def __init__(
        self,
        store: SQLiteRunStore,
    ):
        self.store = store

    # =============================================
    # RUN LIFECYCLE
    # =============================================

    def create_run(
        self,
        goal: str,
    ) -> Run:
        run = Run(
            run_id=new_id("run"),
            goal=goal,
            status=RunStatus.CREATED,
            created_at=utc_now(),
        )

        self.store.create_run(
            run
        )

        self.record_event(
            run_id=run.run_id,
            event_type=EventType.RUN_CREATED,
            data={
                "goal": goal,
            },
        )

        return run

    def start_run(
        self,
        run: Run,
    ) -> Run:
        run.status = RunStatus.RUNNING
        run.started_at = utc_now()

        self.store.update_run(
            run
        )

        self.record_event(
            run_id=run.run_id,
            event_type=EventType.RUN_STARTED,
        )

        return run

    def complete_run(
        self,
        run: Run,
        outcome: str | None = None,
    ) -> Run:
        run.status = RunStatus.COMPLETED
        run.completed_at = utc_now()
        run.outcome = outcome

        self.store.update_run(
            run
        )

        self.record_event(
            run_id=run.run_id,
            event_type=EventType.RUN_COMPLETED,
            data={
                "outcome": outcome,
            },
        )

        return run

    def stuck_run(
        self,
        run: Run,
        outcome: str | None = None,
    ) -> Run:
        run.status = RunStatus.STUCK
        run.completed_at = utc_now()
        run.outcome = outcome

        self.store.update_run(
            run
        )

        self.record_event(
            run_id=run.run_id,
            event_type=EventType.RUN_STUCK,
            data={
                "outcome": outcome,
            },
        )

        return run

    def fail_run(
        self,
        run: Run,
        outcome: str | None = None,
    ) -> Run:
        run.status = RunStatus.FAILED
        run.completed_at = utc_now()
        run.outcome = outcome

        self.store.update_run(
            run
        )

        self.record_event(
            run_id=run.run_id,
            event_type=EventType.RUN_FAILED,
            data={
                "outcome": outcome,
            },
        )

        return run

    def cancel_run(
        self,
        run: Run,
        outcome: str | None = None,
    ) -> Run:
        run.status = RunStatus.CANCELLED
        run.completed_at = utc_now()
        run.outcome = outcome

        self.store.update_run(
            run
        )

        self.record_event(
            run_id=run.run_id,
            event_type=EventType.RUN_CANCELLED,
            data={
                "outcome": outcome,
            },
        )

        return run

    def cancel_step(
        self,
        step: Step,
        outcome: str | None = None,
    ) -> Step:
        step.status = StepStatus.CANCELLED
        step.completed_at = utc_now()
        step.outcome = outcome

        self.store.update_step(
            step
        )

        self.record_event(
            run_id=step.run_id,
            step_id=step.step_id,
            event_type=EventType.STEP_CANCELLED,
            data={
                "outcome": outcome,
            },
        )

        return step

    def max_steps_reached(
        self,
        run: Run,
        outcome: str | None = None,
    ) -> Run:
        run.status = (
            RunStatus.MAX_STEPS_REACHED
        )

        run.completed_at = utc_now()
        run.outcome = outcome

        self.store.update_run(
            run
        )

        self.record_event(
            run_id=run.run_id,
            event_type=(
                EventType.RUN_MAX_STEPS_REACHED
            ),
            data={
                "outcome": outcome,
            },
        )

        return run

    # =============================================
    # STEP LIFECYCLE
    # =============================================

    def start_step(
        self,
        run: Run,
        number: int,
    ) -> Step:
        step = Step(
            step_id=new_id("step"),
            run_id=run.run_id,
            number=number,
            status=StepStatus.RUNNING,
            started_at=utc_now(),
        )

        self.store.create_step(
            step
        )

        run.current_step = number

        self.store.update_run(
            run
        )

        self.record_event(
            run_id=run.run_id,
            step_id=step.step_id,
            event_type=EventType.STEP_STARTED,
            data={
                "step_number": number,
            },
        )

        return step

    def complete_step(
        self,
        step: Step,
        outcome: str | None = None,
    ) -> Step:
        step.status = StepStatus.COMPLETED
        step.completed_at = utc_now()
        step.outcome = outcome

        self.store.update_step(
            step
        )

        self.record_event(
            run_id=step.run_id,
            step_id=step.step_id,
            event_type=EventType.STEP_COMPLETED,
            data={
                "outcome": outcome,
            },
        )

        return step

    def fail_step(
        self,
        step: Step,
        outcome: str | None = None,
    ) -> Step:
        step.status = StepStatus.FAILED
        step.completed_at = utc_now()
        step.outcome = outcome

        self.store.update_step(
            step
        )

        self.record_event(
            run_id=step.run_id,
            step_id=step.step_id,
            event_type=EventType.STEP_FAILED,
            data={
                "outcome": outcome,
            },
        )

        return step

    # =============================================
    # ACTION STATE
    # =============================================

    def set_proposed_action(
        self,
        step: Step,
        action: dict[str, Any],
    ) -> Step:
        step.proposed_action = action

        self.store.update_step(
            step
        )

        self.record_event(
            run_id=step.run_id,
            step_id=step.step_id,
            event_type=EventType.ACTION_PROPOSED,
            data={
                "action": action,
            },
        )

        return step

    # =============================================
    # EVENTS
    # =============================================

    def record_event(
        self,
        run_id: str,
        event_type: EventType,
        step_id: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> RuntimeEvent:
        event = RuntimeEvent(
            event_id=new_id("evt"),
            run_id=run_id,
            step_id=step_id,
            event_type=event_type,
            timestamp=utc_now(),
            data=data or {},
        )

        self.store.append_event(
            event
        )

        return event