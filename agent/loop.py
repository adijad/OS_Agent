from time import sleep

from .executor import ActionExecutor
from .models import create_model_provider
from .policy import PolicyEngine


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

        self.model = create_model_provider(provider=model_provider)

        self.policy = PolicyEngine()

        self.max_steps = max_steps

    def _is_stuck(
        self,
        history: list[dict],
    ) -> bool:
        """
        Detect obvious repeated action cycles.

        Examples:

            Clear -> Seven -> Clear -> Seven -> Clear -> Seven

        or:

            Clear -> Clear -> Clear -> Clear
        """

        if len(history) < 6:
            return False

        recent = []

        for item in history[-6:]:
            recent.append(
                (
                    item["action"].get(
                        "action"
                    ),
                    item.get(
                        "target_name"
                    ),
                )
            )

        # A B A B A B
        if (
            recent[0]
            == recent[2]
            == recent[4]
            and recent[1]
            == recent[3]
            == recent[5]
        ):
            return True

        # A A A A A A
        if len(set(recent)) == 1:
            return True

        return False

    def run(self, goal: str):
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

            # 1. Capture the current computer state
            state = (
                self.computer.capture_state()
            )

            # 2. Give the model:
            #    - current state
            #    - sanitized history
            #
            # The screenshot is deleted immediately after
            # the model has finished using it.
            try:
                proposed = (
                    self.model.choose_action(
                        goal=goal,
                        state=state,
                        history=self._history_for_model(
                            history
                        ),
                    )
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

            # 3. If the model believes the task is complete,
            #    stop the loop.
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

            # 4. Convert model output into the exact
            #    action format understood by the executor.
            action = self._clean_action(
                proposed
            )

            # 5. Resolve the temporary target ID back
            #    to its semantic UI control.
            #
            # This is very useful for debugging.
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

            # 6. Run policy + executor
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

            # 7. Store the full trace internally.
            #
            # The raw action may contain a snapshot-scoped
            # target ID, which is useful for debugging.
            #
            # But _history_for_model() removes those IDs
            # before sending history back to the model.
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

            # Small pause before capturing the new state.
            sleep(0.5)

        print(
            "\n❌ Maximum step limit reached."
        )

        if self._is_stuck(history):
            print(
                "\n⚠ STUCK: repeating action "
                "pattern detected."
            )

            return {
                "status": "stuck",
                "history": history,
            }

        return {
            "status": "max_steps",
            "history": history,
        }


    def _clean_action(
        self,
        proposed: dict,
    ) -> dict:
        """
        Convert the model response into the exact
        action dictionary expected by ActionExecutor.
        """

        action_type = proposed["action"]

        action = {
            "action": action_type,
        }

        if action_type in {
            "click",
            "focus_window",
        }:
            action["target"] = (
                proposed.get("target")
            )

        elif action_type == "type_text":
            action["target"] = (
                proposed.get("target")
            )

            action["text"] = (
                proposed.get("text")
            )

            if (
                "clear_first"
                in proposed
            ):
                action["clear_first"] = (
                    proposed.get(
                        "clear_first"
                    )
                )

        elif action_type == "press_keys":
            action["keys"] = (
                proposed.get("keys")
            )

        elif (
            action_type
            == "launch_application"
        ):
            action["executable"] = (
                proposed.get(
                    "executable"
                )
            )

        return action

    def _get_target_info(
        self,
        action: dict,
        state: dict,
    ):
        """
        Given the model's chosen target ID,
        find the actual semantic control from
        the CURRENT snapshot.

        This lets us verify things like:

        Model says:
            "Click Nine"

        Model target ID actually points to:
            Button 'Seven'

        which would reveal a model grounding error.
        """

        target_id = action.get(
            "target"
        )

        if not target_id:
            return None

        controls = (
            state["semantic"]
            .get("controls", [])
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

        # The target may also be a window,
        # for example with focus_window.
        windows = (
            state["semantic"]
            .get("windows", [])
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

    def _history_for_model(
        self,
        history: list[dict],
    ) -> list[dict]:
        """
        Build a compact history for the model.

        IMPORTANT:
        We deliberately do NOT send old target IDs.

        Target IDs are snapshot-scoped, so an ID like:

            abc123:control:42

        becomes invalid as soon as the next observation
        is captured.

        Sending old IDs back to the model was confusing it.
        """

        model_history = []

        for item in history[-6:]:
            model_history.append(
                {
                    "step": item[
                        "step"
                    ],
                    "action": (
                        item["action"]
                        .get("action")
                    ),
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
                        .get("status")
                    ),
                }
            )

        return model_history