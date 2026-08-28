from time import (
    perf_counter,
    sleep,
)

from observability import (
    get_tracer,
)

from observability.metrics import (
    AgentMetrics,
)

from runtime import (
    ExecutionRuntime,
    SQLiteRunStore,
)

from .executor import ActionExecutor
from .models import create_model_provider
from .policy import PolicyEngine


tracer = get_tracer(
    "os_agent.agent"
)


class AgentLoop:
    def __init__(
        self,
        computer,
        *,
        model_provider: str | None = None,
        max_steps: int = 25,
        runtime: ExecutionRuntime | None = None,
    ):
        self.computer = computer

        self.executor = ActionExecutor(
            computer
        )

        self.model = create_model_provider(
            provider=model_provider
        )

        self.policy = PolicyEngine()

        self.metrics = AgentMetrics()

        self.runtime = (
            runtime
            or ExecutionRuntime(
                SQLiteRunStore(
                    "data/os_agent.db"
                )
            )
        )

        self.max_steps = max_steps

    # =====================================================
    # AGENT RUN
    # =====================================================

    def run(
        self,
        goal: str,
    ):
        history = []

        # =================================================
        # EXECUTION RUNTIME
        #
        # One user goal corresponds to one persistent
        # runtime Run.
        # =================================================

        runtime_run = (
            self.runtime.create_run(
                goal
            )
        )

        self.runtime.start_run(
            runtime_run
        )

        active_runtime_step = None

        run_provider = "unknown"
        run_model = "unknown"

        # =================================================
        # RUN-LEVEL TELEMETRY ACCUMULATORS
        # =================================================

        model_calls = 0
        executed_actions = 0
        steps_attempted = 0

        total_input_tokens = 0
        total_output_tokens = 0
        total_tokens = 0

        total_cached_input_tokens = 0
        total_cache_creation_input_tokens = 0
        total_reasoning_tokens = 0

        total_model_latency_ms = 0.0
        total_policy_latency_ms = 0.0
        total_executor_latency_ms = 0.0
        total_observe_latency_ms = 0.0

        run_status = "unknown"

        run_started = perf_counter()

        # =================================================
        # ROOT RUN SPAN
        #
        # One user goal should correspond to one trace.
        #
        # All step spans created inside this context
        # automatically become children of this run span.
        # =================================================

        with tracer.start_as_current_span(
            "os_agent.run"
        ) as run_span:

            run_span.set_attribute(
                "os_agent.runtime.run_id",
                runtime_run.run_id,
            )

            try:
                print(
                    "\n============================"
                )
                print(
                    "OS AGENT"
                )
                print(
                    "============================"
                )
                print(
                    f"Goal: {goal}"
                )

                # =========================================
                # MAIN AGENT LOOP
                # =========================================

                for step in range(
                    1,
                    self.max_steps + 1,
                ):
                    steps_attempted = step

                    # =====================================
                    # RUNTIME STEP
                    #
                    # Each real AgentLoop iteration owns
                    # one persistent runtime Step.
                    # =====================================

                    runtime_step = (
                        self.runtime.start_step(
                            runtime_run,
                            number=step,
                        )
                    )

                    active_runtime_step = (
                        runtime_step
                    )

                    # =====================================
                    # STEP SPAN
                    #
                    # One complete:
                    #
                    # observe
                    #     ↓
                    # reason
                    #     ↓
                    # act
                    #
                    # cycle.
                    # =====================================

                    with tracer.start_as_current_span(
                        "os_agent.step"
                    ) as step_span:

                        step_span.set_attribute(
                            "os_agent.step.number",
                            step,
                        )

                        step_span.set_attribute(
                            "os_agent.runtime.run_id",
                            runtime_run.run_id,
                        )

                        step_span.set_attribute(
                            "os_agent.runtime.step_id",
                            runtime_step.step_id,
                        )

                        print(
                            f"\n---------- STEP "
                            f"{step} ----------"
                        )

                        # ---------------------------------
                        # 1. Observe current computer state
                        # ---------------------------------

                        with tracer.start_as_current_span(
                            "os_agent.computer.observe"
                        ) as observe_span:

                            observe_started = (
                                perf_counter()
                            )

                            try:
                                state = (
                                    self.computer
                                    .capture_state()
                                )

                            finally:
                                observe_latency_ms = (
                                    (
                                        perf_counter()
                                        - observe_started
                                    )
                                    * 1000
                                )

                                total_observe_latency_ms += (
                                    observe_latency_ms
                                )

                                self.metrics.record_observation(
                                    observe_latency_ms
                                )

                                observe_span.set_attribute(
                                    (
                                        "os_agent.observe."
                                        "latency_ms"
                                    ),
                                    observe_latency_ms,
                                )

                        # ---------------------------------
                        # 2. Ask the model for exactly one
                        #    next action.
                        #
                        # Because this span is created
                        # inside the step span, it
                        # automatically becomes its child.
                        # ---------------------------------

                        try:
                            with (
                                tracer
                                .start_as_current_span(
                                    "os_agent.model."
                                    "choose_action"
                                )
                            ) as model_span:

                                model_started = (
                                    perf_counter()
                                )

                                model_result = (
                                    self.model
                                    .choose_action(
                                        goal=goal,
                                        state=state,
                                        history=(
                                            self
                                            ._history_for_model(
                                                history
                                            )
                                        ),
                                    )
                                )

                                model_latency_ms = (
                                    (
                                        perf_counter()
                                        - model_started
                                    )
                                    * 1000
                                )

                                proposed = (
                                    model_result.action
                                )

                                usage = (
                                    model_result.usage
                                )

                                proposed_action = (
                                    proposed.get(
                                        "action",
                                        "unknown",
                                    )
                                )

                                # =========================
                                # PER-MODEL-CALL TELEMETRY
                                # =========================

                                model_span.set_attribute(
                                    (
                                        "os_agent.model."
                                        "provider"
                                    ),
                                    model_result.provider,
                                )

                                model_span.set_attribute(
                                    "os_agent.model.name",
                                    model_result.model,
                                )

                                model_span.set_attribute(
                                    (
                                        "os_agent.step."
                                        "number"
                                    ),
                                    step,
                                )

                                model_span.set_attribute(
                                    (
                                        "os_agent.model."
                                        "latency_ms"
                                    ),
                                    model_latency_ms,
                                )

                                model_span.set_attribute(
                                    (
                                        "os_agent.model."
                                        "input_tokens"
                                    ),
                                    usage.input_tokens,
                                )

                                model_span.set_attribute(
                                    (
                                        "os_agent.model."
                                        "output_tokens"
                                    ),
                                    usage.output_tokens,
                                )

                                model_span.set_attribute(
                                    (
                                        "os_agent.model."
                                        "total_tokens"
                                    ),
                                    usage.total_tokens,
                                )

                                model_span.set_attribute(
                                    (
                                        "os_agent.model."
                                        "cached_input_tokens"
                                    ),
                                    (
                                        usage
                                        .cached_input_tokens
                                    ),
                                )

                                model_span.set_attribute(
                                    (
                                        "os_agent.model."
                                        "cache_creation_"
                                        "input_tokens"
                                    ),
                                    (
                                        usage
                                        .cache_creation_input_tokens
                                    ),
                                )

                                model_span.set_attribute(
                                    (
                                        "os_agent.model."
                                        "reasoning_tokens"
                                    ),
                                    usage.reasoning_tokens,
                                )

                                model_span.set_attribute(
                                    (
                                        "os_agent.model."
                                        "proposed_action"
                                    ),
                                    proposed_action,
                                )

                                # =========================
                                # UPDATE RUN TOTALS
                                # =========================

                                model_calls += 1

                                total_model_latency_ms += (
                                    model_latency_ms
                                )

                                total_input_tokens += (
                                    usage.input_tokens
                                )

                                total_output_tokens += (
                                    usage.output_tokens
                                )

                                total_tokens += (
                                    usage.total_tokens
                                )

                                (
                                    total_cached_input_tokens
                                ) += (
                                    usage
                                    .cached_input_tokens
                                )

                                (
                                    total_cache_creation_input_tokens
                                ) += (
                                    usage
                                    .cache_creation_input_tokens
                                )

                                (
                                    total_reasoning_tokens
                                ) += (
                                    usage
                                    .reasoning_tokens
                                )

                                self.metrics.record_model_call(
                                    provider=(
                                        model_result.provider
                                    ),
                                    model=(
                                        model_result.model
                                    ),
                                    latency_ms=(
                                        model_latency_ms
                                    ),
                                    input_tokens=(
                                        usage.input_tokens
                                    ),
                                    output_tokens=(
                                        usage.output_tokens
                                    ),
                                    total_tokens=(
                                        usage.total_tokens
                                    ),
                                )

                                run_provider = (
                                    model_result.provider
                                )

                                run_model = (
                                    model_result.model
                                )

                                # -------------------------
                                # Provider/model metadata
                                # also belongs on the root
                                # run span.
                                # -------------------------

                                run_span.set_attribute(
                                    "os_agent.run.provider",
                                    run_provider,
                                )

                                run_span.set_attribute(
                                    "os_agent.run.model",
                                    run_model,
                                )

                        finally:
                            # Temporary screenshot/state
                            # resources are no longer needed
                            # after the model has consumed
                            # the observation.
                            self.computer.cleanup_state(
                                state
                            )

                        # =================================
                        # STEP METADATA
                        # =================================

                        proposed_action = (
                            proposed.get(
                                "action",
                                "unknown",
                            )
                        )

                        step_span.set_attribute(
                            (
                                "os_agent.step."
                                "proposed_action"
                            ),
                            proposed_action,
                        )

                        print(
                            f"Reason: "
                            f"{proposed.get('reason')}"
                        )

                        print(
                            f"Proposed action: "
                            f"{proposed_action}"
                        )

                        # ---------------------------------
                        # Convert the provider response
                        # into the normalized OS Agent
                        # semantic action BEFORE writing
                        # it into persistent runtime state.
                        # ---------------------------------

                        action = (
                            self._clean_action(
                                proposed
                            )
                        )

                        self.runtime.set_proposed_action(
                            runtime_step,
                            action,
                        )

                        # ---------------------------------
                        # 3. Finish if the model believes
                        #    the requested goal has been
                        #    satisfied.
                        # ---------------------------------

                        if (
                            proposed_action
                            == "finish"
                        ):
                            answer = (
                                proposed.get(
                                    "answer"
                                )
                            )

                            run_status = "success"

                            step_span.set_attribute(
                                (
                                    "os_agent.step."
                                    "outcome"
                                ),
                                "finish",
                            )

                            print(
                                "\n✅ GOAL COMPLETE"
                            )

                            if answer:
                                print(
                                    f"Answer: {answer}"
                                )

                            self.runtime.complete_step(
                                runtime_step,
                                outcome="finish",
                            )

                            active_runtime_step = None

                            self.runtime.complete_run(
                                runtime_run,
                                outcome=answer,
                            )

                            return {
                                "status": "success",
                                "answer": answer,
                                "history": history,
                                "run_id": (
                                    runtime_run.run_id
                                ),
                            }

                        # ---------------------------------
                        # 4. Action has already been
                        #    normalized above.
                        # ---------------------------------

                        # ---------------------------------
                        # 5. Ground target IDs back to the
                        #    semantic observation.
                        # ---------------------------------

                        target_info = (
                            self._get_target_info(
                                action,
                                state,
                            )
                        )

                        if target_info:
                            print(
                                "Grounded target: "
                                f"{target_info['role']} "
                                f"{target_info['name']!r}"
                            )

                        # ---------------------------------
                        # 6. Policy check + physical
                        #    execution.
                        # ---------------------------------

                        try:
                            # =============================
                            # POLICY SPAN
                            # =============================

                            with tracer.start_as_current_span(
                                "os_agent.policy.check"
                            ) as policy_span:

                                policy_started = (
                                    perf_counter()
                                )

                                try:
                                    self.policy.check(
                                        action=action,
                                        state=state,
                                    )

                                    policy_span.set_attribute(
                                        (
                                            "os_agent.policy."
                                            "outcome"
                                        ),
                                        "allow",
                                    )

                                finally:
                                    policy_latency_ms = (
                                        (
                                            perf_counter()
                                            - policy_started
                                        )
                                        * 1000
                                    )

                                    (
                                        total_policy_latency_ms
                                    ) += (
                                        policy_latency_ms
                                    )

                                    policy_span.set_attribute(
                                        (
                                            "os_agent.policy."
                                            "latency_ms"
                                        ),
                                        policy_latency_ms,
                                    )

                                    policy_span.set_attribute(
                                        (
                                            "os_agent.policy."
                                            "action_type"
                                        ),
                                        action.get(
                                            "action",
                                            "unknown",
                                        ),
                                    )

                            # =============================
                            # EXECUTOR SPAN
                            # =============================

                            with tracer.start_as_current_span(
                                "os_agent.executor.execute"
                            ) as executor_span:

                                executor_started = (
                                    perf_counter()
                                )

                                executor_status = "error"

                                try:
                                    result = (
                                        self.executor.execute(
                                            action
                                        )
                                    )

                                    executor_status = (
                                        result.get(
                                            "status",
                                            "unknown",
                                        )
                                    )

                                    executor_span.set_attribute(
                                        (
                                            "os_agent.executor."
                                            "status"
                                        ),
                                        executor_status,
                                    )

                                finally:
                                    executor_latency_ms = (
                                        (
                                            perf_counter()
                                            - executor_started
                                        )
                                        * 1000
                                    )

                                    (
                                        total_executor_latency_ms
                                    ) += (
                                        executor_latency_ms
                                    )

                                    executor_span.set_attribute(
                                        (
                                            "os_agent.executor."
                                            "latency_ms"
                                        ),
                                        executor_latency_ms,
                                    )

                                    executor_span.set_attribute(
                                        (
                                            "os_agent.executor."
                                            "action_type"
                                        ),
                                        action.get(
                                            "action",
                                            "unknown",
                                        ),
                                    )

                                    self.metrics.record_action(
                                        action_type=(
                                            action.get(
                                                "action",
                                                "unknown",
                                            )
                                        ),
                                        status=(
                                            executor_status
                                        ),
                                        latency_ms=(
                                            executor_latency_ms
                                        ),
                                    )

                            # Only increment this AFTER the
                            # action actually reaches the
                            # executor.
                            executed_actions += 1

                        except KeyboardInterrupt:
                            # -----------------------------------------
                            # USER-INITIATED CANCELLATION
                            #
                            # Ctrl+C is not a software failure.
                            #
                            # Persist the active Step and Run as
                            # CANCELLED before allowing the interrupt
                            # to propagate back to the CLI session.
                            # -----------------------------------------

                            run_status = "cancelled"

                            cancellation_reason = (
                                "Interrupted by user"
                            )

                            if (
                                active_runtime_step
                                is not None
                                and active_runtime_step.completed_at
                                is None
                            ):
                                self.runtime.cancel_step(
                                    active_runtime_step,
                                    outcome=cancellation_reason,
                                )

                            self.runtime.cancel_run(
                                runtime_run,
                                outcome=cancellation_reason,
                            )

                            raise

                        except Exception as exc:
                            run_status = "error"

                            error = (
                                f"{type(exc).__name__}: "
                                f"{exc}"
                            )

                            if (
                                active_runtime_step
                                is not None
                                and active_runtime_step.completed_at
                                is None
                            ):
                                self.runtime.fail_step(
                                    active_runtime_step,
                                    outcome=error,
                                )

                            self.runtime.fail_run(
                                runtime_run,
                                outcome=error,
                            )

                            raise

                        # A model "finish" decision does
                        # not count as a physical action.
                        #
                        # Everything reaching this point
                        # represents an attempted computer
                        # action.

                        step_span.set_attribute(
                            (
                                "os_agent.step."
                                "executor_status"
                            ),
                            result.get(
                                "status",
                                "unknown",
                            ),
                        )

                        # ---------------------------------
                        # 7. Store FULL internal trace.
                        #
                        # Raw snapshot target IDs can remain
                        # here for debugging.
                        #
                        # _history_for_model() sanitizes
                        # them before sending historical
                        # context back to the model.
                        # ---------------------------------

                        history.append(
                            {
                                "step": step,

                                "reason": (
                                    proposed.get(
                                        "reason"
                                    )
                                ),

                                "action": action,

                                "target_name": (
                                    target_info.get(
                                        "name"
                                    )
                                    if target_info
                                    else None
                                ),

                                "target_role": (
                                    target_info.get(
                                        "role"
                                    )
                                    if target_info
                                    else None
                                ),

                                "result": result,
                            }
                        )

                        print(
                            f"Result: {result}"
                        )

                        # =================================
                        # RUNTIME STEP OUTCOME
                        #
                        # An executor error means the Step
                        # failed, but the overall Run may
                        # still continue and recover on the
                        # next iteration.
                        # =================================

                        runtime_result_status = (
                            result.get(
                                "status",
                                "unknown",
                            )
                        )

                        if (
                            runtime_result_status
                            == "error"
                        ):
                            self.runtime.fail_step(
                                runtime_step,
                                outcome=(
                                    result.get("error")
                                    or "action_error"
                                ),
                            )

                            telemetry_step_outcome = (
                                "failed"
                            )

                        else:
                            self.runtime.complete_step(
                                runtime_step,
                                outcome=(
                                    runtime_result_status
                                ),
                            )

                            telemetry_step_outcome = (
                                "continue"
                            )

                        active_runtime_step = None

                        # ---------------------------------
                        # 8. Detect repeated/stuck
                        #    behavior immediately.
                        # ---------------------------------

                        if self._is_stuck(
                            history
                        ):
                            run_status = "stuck"

                            self.runtime.stuck_run(
                                runtime_run,
                                outcome=(
                                    "Repeated action "
                                    "pattern detected"
                                ),
                            )

                            step_span.set_attribute(
                                (
                                    "os_agent.step."
                                    "outcome"
                                ),
                                "stuck",
                            )

                            print(
                                "\n⚠ STUCK: repeating "
                                "action pattern detected."
                            )

                            return {
                                "status": "stuck",
                                "history": history,
                                "run_id": (
                                    runtime_run.run_id
                                ),
                            }

                        # ---------------------------------
                        # This iteration completed.
                        #
                        # The telemetry outcome should
                        # reflect whether this Step actually
                        # completed or failed.
                        # ---------------------------------

                        step_span.set_attribute(
                            (
                                "os_agent.step."
                                "outcome"
                            ),
                            telemetry_step_outcome,
                        )

                    # =====================================
                    # STEP SPAN ENDS HERE
                    # =====================================

                    # Give the interface a moment to
                    # update before observing again.
                    sleep(0.5)

                # =========================================
                # MAXIMUM STEP LIMIT
                # =========================================

                run_status = "max_steps"

                self.runtime.max_steps_reached(
                    runtime_run,
                    outcome=(
                        "Maximum step limit reached"
                    ),
                )

                print(
                    "\n❌ Maximum step limit reached."
                )

                return {
                    "status": "max_steps",
                    "history": history,
                    "run_id": runtime_run.run_id,
                }

            except Exception as exc:
                # -----------------------------------------
                # Preserve unexpected failure as the final
                # runtime + telemetry status.
                #
                # A currently active runtime Step must not
                # remain RUNNING after a normal propagated
                # Python exception.
                # -----------------------------------------

                run_status = "error"

                error = (
                    f"{type(exc).__name__}: "
                    f"{exc}"
                )

                if (
                    active_runtime_step
                    is not None
                    and active_runtime_step.completed_at
                    is None
                ):
                    self.runtime.fail_step(
                        active_runtime_step,
                        outcome=error,
                    )

                self.runtime.fail_run(
                    runtime_run,
                    outcome=error,
                )

                raise

            finally:
                # =========================================
                # FINAL RUN-LEVEL TELEMETRY
                #
                # This executes for:
                #
                # success
                # stuck
                # max_steps
                # exception
                # =========================================

                run_elapsed_ms = (
                    (
                        perf_counter()
                        - run_started
                    )
                    * 1000
                )

                self.metrics.record_run(
                    provider=run_provider,
                    model=run_model,
                    status=run_status,
                    duration_ms=run_elapsed_ms,
                    steps=steps_attempted,
                )

                run_span.set_attribute(
                    "os_agent.run.status",
                    run_status,
                )

                run_span.set_attribute(
                    "os_agent.run.steps",
                    steps_attempted,
                )

                run_span.set_attribute(
                    (
                        "os_agent.run."
                        "model_calls"
                    ),
                    model_calls,
                )

                run_span.set_attribute(
                    (
                        "os_agent.run."
                        "executed_actions"
                    ),
                    executed_actions,
                )

                run_span.set_attribute(
                    (
                        "os_agent.run."
                        "input_tokens"
                    ),
                    total_input_tokens,
                )

                run_span.set_attribute(
                    (
                        "os_agent.run."
                        "output_tokens"
                    ),
                    total_output_tokens,
                )

                run_span.set_attribute(
                    (
                        "os_agent.run."
                        "total_tokens"
                    ),
                    total_tokens,
                )

                run_span.set_attribute(
                    (
                        "os_agent.run."
                        "cached_input_tokens"
                    ),
                    total_cached_input_tokens,
                )

                run_span.set_attribute(
                    (
                        "os_agent.run."
                        "cache_creation_input_tokens"
                    ),
                    (
                        total_cache_creation_input_tokens
                    ),
                )

                run_span.set_attribute(
                    (
                        "os_agent.run."
                        "reasoning_tokens"
                    ),
                    total_reasoning_tokens,
                )

                run_span.set_attribute(
                    (
                        "os_agent.run."
                        "model_latency_ms"
                    ),
                    total_model_latency_ms,
                )

                run_span.set_attribute(
                    (
                        "os_agent.run."
                        "observe_latency_ms"
                    ),
                    total_observe_latency_ms,
                )

                run_span.set_attribute(
                    (
                        "os_agent.run."
                        "policy_latency_ms"
                    ),
                    total_policy_latency_ms,
                )

                run_span.set_attribute(
                    (
                        "os_agent.run."
                        "executor_latency_ms"
                    ),
                    total_executor_latency_ms,
                )

                accounted_latency_ms = (
                    total_model_latency_ms
                    + total_observe_latency_ms
                    + total_policy_latency_ms
                    + total_executor_latency_ms
                )

                unattributed_latency_ms = max(
                    0.0,
                    run_elapsed_ms
                    - accounted_latency_ms,
                )

                run_span.set_attribute(
                    (
                        "os_agent.run."
                        "unattributed_latency_ms"
                    ),
                    unattributed_latency_ms,
                )

                run_span.set_attribute(
                    (
                        "os_agent.run."
                        "elapsed_ms"
                    ),
                    run_elapsed_ms,
                )

    # =====================================================
    # ACTION CLEANING
    # =====================================================

    def _clean_action(
        self,
        proposed: dict,
    ) -> dict:
        """
        Convert the provider's structured response
        into the exact action dictionary expected
        by ActionExecutor.

        This normalized semantic action is also the
        action persisted by the execution runtime.
        """

        action_type = proposed[
            "action"
        ]

        action = {
            "action": action_type,
        }

        # -----------------------------
        # Mouse / semantic target
        # -----------------------------

        if action_type in {
            "click",
            "focus_window",
        }:
            action["target"] = (
                proposed.get(
                    "target"
                )
            )

        # -----------------------------
        # Literal text input
        # -----------------------------

        elif action_type == "type_text":
            action["target"] = (
                proposed.get(
                    "target"
                )
            )

            action["text"] = (
                proposed.get(
                    "text"
                )
            )

            action["clear_first"] = bool(
                proposed.get(
                    "clear_first",
                    False,
                )
            )

        # -----------------------------
        # One semantic special key
        #
        # Example:
        #
        # ENTER
        # TAB
        # ESC
        # -----------------------------

        elif action_type == "press_key":
            action["key"] = (
                proposed.get(
                    "key"
                )
            )

        # -----------------------------
        # Structured keyboard shortcut
        #
        # Example:
        #
        # ["CTRL", "L"]
        # ["CTRL", "SHIFT", "S"]
        # -----------------------------

        elif action_type == "hotkey":
            action["keys"] = (
                proposed.get(
                    "keys"
                )
            )

        # -----------------------------
        # Application launch
        # -----------------------------

        elif (
            action_type
            == "open_application"
        ):
            action["application"] = (
                proposed.get(
                    "application"
                )
            )

        return action

    # =====================================================
    # TARGET GROUNDING
    # =====================================================

    def _get_target_info(
        self,
        action: dict,
        state: dict,
    ):
        """
        Resolve the model's CURRENT snapshot target ID
        back to its semantic control/window.

        This lets us detect grounding problems such as:

            Reason:
                Click Nine

            Actual selected target:
                Button 'Seven'
        """

        target_id = action.get(
            "target"
        )

        # Keyboard actions such as press_key/hotkey
        # do not have semantic target IDs.
        if not target_id:
            return None

        controls = (
            state["semantic"]
            .get(
                "controls",
                [],
            )
        )

        for control in controls:
            if (
                control.get("id")
                == target_id
            ):
                return {
                    "id": target_id,

                    "name": control.get(
                        "name"
                    ),

                    "role": control.get(
                        "role"
                    ),
                }

        # Target may also be a top-level window.

        windows = (
            state["semantic"]
            .get(
                "windows",
                [],
            )
        )

        for window in windows:
            if (
                window.get("id")
                == target_id
            ):
                return {
                    "id": target_id,

                    "name": window.get(
                        "title"
                    ),

                    "role": "Window",
                }

        return None

    # =====================================================
    # MODEL HISTORY
    # =====================================================

    def _history_for_model(
        self,
        history: list[dict],
    ) -> list[dict]:
        """
        Build compact history for the model.

        Important:

        We DO NOT send old snapshot target IDs.

        Those IDs expire after every new observation.

        We DO send semantic information such as:

            click Button 'Nine'

            type_text "24+83"

            press_key ENTER

            hotkey CTRL+L

        This gives the model useful historical context
        without exposing stale references.
        """

        model_history = []

        for item in history[-6:]:
            action = item[
                "action"
            ]

            action_type = action.get(
                "action"
            )

            entry = {
                "step": item[
                    "step"
                ],

                "action": action_type,

                "target_name": (
                    item.get(
                        "target_name"
                    )
                ),

                "target_role": (
                    item.get(
                        "target_role"
                    )
                ),

                "executor_status": (
                    item["result"]
                    .get(
                        "status"
                    )
                ),
            }

            # -----------------------------------------
            # Preserve keyboard/text semantics
            # -----------------------------------------

            if action_type == "type_text":
                entry["text"] = (
                    action.get(
                        "text"
                    )
                )

            elif (
                action_type
                == "press_key"
            ):
                entry["key"] = (
                    action.get(
                        "key"
                    )
                )

            elif (
                action_type
                == "hotkey"
            ):
                entry["keys"] = (
                    action.get(
                        "keys"
                    )
                )

            elif (
                action_type
                == "open_application"
            ):
                entry[
                    "application"
                ] = action.get(
                    "application"
                )

            model_history.append(
                entry
            )

        return model_history

    # =====================================================
    # ACTION SIGNATURE
    # =====================================================

    def _action_signature(
        self,
        item: dict,
    ):
        """
        Create a comparable semantic representation
        of an action.

        This is used by stuck detection.

        We cannot simply compare:

            action type + target_name

        because keyboard actions do not necessarily
        have targets.

        Examples:

            click Nine
                -> ("click", "Nine")

            type_text "24+83"
                -> ("type_text", "Calculator", "24+83")

            press_key ENTER
                -> ("press_key", "ENTER")

            hotkey CTRL+L
                -> ("hotkey", ("CTRL", "L"))
        """

        action = item[
            "action"
        ]

        action_type = action.get(
            "action"
        )

        # -----------------------------
        # Target-based actions
        # -----------------------------

        if action_type in {
            "click",
            "focus_window",
        }:
            return (
                action_type,
                item.get(
                    "target_name"
                ),
            )

        # -----------------------------
        # Text input
        # -----------------------------

        if action_type == "type_text":
            return (
                action_type,

                item.get(
                    "target_name"
                ),

                action.get(
                    "text"
                ),
            )

        # -----------------------------
        # Single key
        # -----------------------------

        if action_type == "press_key":
            return (
                action_type,

                action.get(
                    "key"
                ),
            )

        # -----------------------------
        # Hotkey
        # -----------------------------

        if action_type == "hotkey":
            return (
                action_type,

                tuple(
                    action.get(
                        "keys"
                    )
                    or []
                ),
            )

        # -----------------------------
        # Application launch
        # -----------------------------

        if (
            action_type
            == "open_application"
        ):
            return (
                action_type,

                action.get(
                    "application"
                ),
            )

        return (
            action_type,
        )

    # =====================================================
    # STUCK DETECTION
    # =====================================================

    def _is_stuck(
        self,
        history: list[dict],
    ) -> bool:
        """
        Detect obvious repeated action cycles.

        Pattern 1:

            A B A B A B

        Example:

            Seven
            Clear
            Seven
            Clear
            Seven
            Clear


        Pattern 2:

            A A A A A A

        Example:

            press_key ENTER
            press_key ENTER
            press_key ENTER
            ...
        """

        if len(history) < 6:
            return False

        recent = [
            self._action_signature(
                item
            )
            for item
            in history[-6:]
        ]

        # -----------------------------------------
        # A B A B A B
        # -----------------------------------------

        if (
            recent[0]
            == recent[2]
            == recent[4]
            and
            recent[1]
            == recent[3]
            == recent[5]
        ):
            return True

        # -----------------------------------------
        # A A A A A A
        # -----------------------------------------

        if len(set(recent)) == 1:
            return True

        return False