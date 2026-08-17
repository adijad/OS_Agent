from .executor import ActionExecutor
from .models import create_model_provider
from .policy import PolicyEngine
from time import (
    perf_counter,
    sleep,
)

from observability import (
    get_tracer,
)

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
    ):
        self.computer = computer

        self.executor = ActionExecutor(
            computer
        )

        self.model = create_model_provider(
            provider=model_provider
        )

        self.policy = PolicyEngine()

        self.max_steps = max_steps

    def run(
        self,
        goal: str,
    ):
        history = []

        print("\n============================")
        print("OS AGENT")
        print("============================")
        print(f"Goal: {goal}")

        for step in range(
            1,
            self.max_steps + 1,
        ):
            print(
                f"\n---------- STEP {step} ----------"
            )

            # -------------------------------------------------
            # 1. Observe current computer state
            # -------------------------------------------------

            state = (
                self.computer.capture_state()
            )

            # -------------------------------------------------
            # 2. Ask the model for exactly one next action
            #
            # We send sanitized history rather than the
            # full internal trace.
            #
            # The temporary screenshot is deleted as soon
            # as the model has finished using it.
            # -------------------------------------------------

            try:
                with tracer.start_as_current_span(
                    "os_agent.model.choose_action"
                ) as model_span:

                    started = perf_counter()

                    model_result = (
                        self.model.choose_action(
                            goal=goal,
                            state=state,
                            history=(
                                self._history_for_model(
                                    history
                                )
                            ),
                        )
                    )

                    model_latency_ms = (
                        perf_counter()
                        - started
                    ) * 1000

                    proposed = (
                        model_result.action
                    )

                    usage = (
                        model_result.usage
                    )

                    model_span.set_attribute(
                        "os_agent.model.provider",
                        model_result.provider,
                    )

                    model_span.set_attribute(
                        "os_agent.model.name",
                        model_result.model,
                    )

                    model_span.set_attribute(
                        "os_agent.step.number",
                        step,
                    )

                    model_span.set_attribute(
                        "os_agent.model.latency_ms",
                        model_latency_ms,
                    )

                    model_span.set_attribute(
                        "os_agent.model.input_tokens",
                        usage.input_tokens,
                    )

                    model_span.set_attribute(
                        "os_agent.model.output_tokens",
                        usage.output_tokens,
                    )

                    model_span.set_attribute(
                        "os_agent.model.total_tokens",
                        usage.total_tokens,
                    )

                    model_span.set_attribute(
                        "os_agent.model.cached_input_tokens",
                        usage.cached_input_tokens,
                    )

                    model_span.set_attribute(
                        "os_agent.model.reasoning_tokens",
                        usage.reasoning_tokens,
                    )

                    model_span.set_attribute(
                        "os_agent.model.proposed_action",
                        proposed.get(
                            "action",
                            "unknown",
                        ),
                    )

            finally:
                self.computer.cleanup_state(
                    state
                )

            print(
                f"Reason: "
                f"{proposed.get('reason')}"
            )

            print(
                f"Proposed action: "
                f"{proposed.get('action')}"
            )

            # -------------------------------------------------
            # 3. Finish if the model believes the user's
            #    requested goal is already satisfied.
            # -------------------------------------------------

            if (
                proposed.get("action")
                == "finish"
            ):
                answer = proposed.get(
                    "answer"
                )

                print("\n✅ GOAL COMPLETE")

                if answer:
                    print(
                        f"Answer: {answer}"
                    )

                return {
                    "status": "success",
                    "answer": answer,
                    "history": history,
                }

            # -------------------------------------------------
            # 4. Convert provider output into our internal
            #    OS Agent action format.
            # -------------------------------------------------

            action = self._clean_action(
                proposed
            )

            # -------------------------------------------------
            # 5. Ground target IDs back to semantic controls.
            #
            # click, type_text, and focus_window may contain
            # a temporary snapshot target.
            #
            # press_key and hotkey do not require a target.
            # -------------------------------------------------

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

            # -------------------------------------------------
            # 6. Policy check + physical execution
            # -------------------------------------------------

            try:
                self.policy.check(
                    action=action,
                    state=state,
                )

                result = (
                    self.executor.execute(
                        action
                    )
                )

            except Exception as exc:
                result = {
                    "status": "error",
                    "error": (
                        f"{type(exc).__name__}: "
                        f"{exc}"
                    ),
                }

            # -------------------------------------------------
            # 7. Store FULL internal trace
            #
            # This can keep the raw target ID because it is
            # useful for debugging.
            #
            # _history_for_model() will sanitize it before
            # sending history back to the LLM.
            # -------------------------------------------------

            history.append(
                {
                    "step": step,

                    "reason": proposed.get(
                        "reason"
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

            # -------------------------------------------------
            # 8. Detect repeated/stuck behavior IMMEDIATELY
            #
            # We do this inside the loop, after every action.
            #
            # Example:
            #
            # Clear -> Seven -> Clear -> Seven
            #       -> Clear -> Seven
            #
            # should stop here instead of consuming all
            # 25 model calls.
            # -------------------------------------------------

            if self._is_stuck(
                history
            ):
                print(
                    "\n⚠ STUCK: repeating action "
                    "pattern detected."
                )

                return {
                    "status": "stuck",
                    "history": history,
                }

            # Give the UI a moment to update before
            # observing the next state.
            sleep(0.5)

        # -------------------------------------------------
        # Max steps reached without finish or stuck
        # -------------------------------------------------

        print(
            "\n❌ Maximum step limit reached."
        )

        return {
            "status": "max_steps",
            "history": history,
        }

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
        # Launch
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