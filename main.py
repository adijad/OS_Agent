import argparse

from agent.loop import AgentLoop

from computer import (
    Computer,
)

from observability import (
    configure_telemetry,
    ensure_observability,
    shutdown_telemetry,
)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--provider",
        choices=[
            "openai",
            "anthropic",
        ],
        default=None,
    )

    args = parser.parse_args()

    # =============================================
    # OBSERVABILITY PREFLIGHT
    #
    # Do not begin an OS Agent session unless
    # telemetry infrastructure is available.
    # =============================================

    try:
        ensure_observability()

    except RuntimeError as exc:
        print()
        print(
            "❌ Cannot start OS Agent"
        )
        print(
            str(exc)
        )
        return

    # =============================================
    # TELEMETRY
    #
    # Configure telemetry once for the entire
    # CLI session.
    # =============================================

    configure_telemetry()

    try:
        # =========================================
        # SESSION INITIALIZATION
        #
        # Computer and AgentLoop are initialized
        # once and reused across multiple goals.
        # =========================================

        computer = Computer()

        agent = AgentLoop(
            computer,
            model_provider=args.provider,
            max_steps=20,
        )

        print()
        print(
            "============================"
        )
        print(
            "OS AGENT SESSION"
        )
        print(
            "============================"
        )
        print(
            "Enter a goal to begin."
        )
        print(
            "Type 'exit' to stop."
        )
        print(
            "You can also press Ctrl+C."
        )

        # =========================================
        # MULTI-GOAL SESSION LOOP
        # =========================================

        while True:
            print()

            try:
                goal = input(
                    "What would you like me to do?\n> "
                ).strip()

            except KeyboardInterrupt:
                print()
                print()
                print(
                    "Stopping OS Agent..."
                )
                break

            # =====================================
            # EXIT COMMAND
            # =====================================

            if (
                goal.lower()
                == "exit"
            ):
                print()
                print(
                    "Stopping OS Agent..."
                )
                break

            # =====================================
            # EMPTY INPUT
            # =====================================

            if not goal:
                print(
                    "No goal provided."
                )
                continue

            # =====================================
            # EXECUTE ONE DURABLE RUN
            #
            # AgentLoop.run() creates exactly one
            # persistent runtime Run for this goal.
            # =====================================

            try:
                result = agent.run(
                    goal
                )

            except KeyboardInterrupt:
                print()
                print()
                print(
                    "Stopping OS Agent..."
                )
                break

            except Exception as exc:
                # AgentLoop is responsible for marking
                # its current runtime Run as FAILED
                # before propagating the exception.
                #
                # The CLI session itself can remain alive
                # so the user can issue another goal.

                print()
                print(
                    "❌ Run failed"
                )
                print(
                    f"{type(exc).__name__}: "
                    f"{exc}"
                )
                print()
                print(
                    "OS Agent session is still active."
                )

                continue

            # =====================================
            # RUN SUMMARY
            # =====================================

            print()
            print(
                "----------------------------"
            )
            print(
                "RUN FINISHED"
            )
            print(
                "----------------------------"
            )

            print(
                "Status: "
                f"{result.get('status')}"
            )

            run_id = result.get(
                "run_id"
            )

            if run_id:
                print(
                    f"Run ID: {run_id}"
                )

            answer = result.get(
                "answer"
            )

            if answer:
                print(
                    f"Answer: {answer}"
                )

            print(
                "Ready for another goal."
            )

    finally:
        # =========================================
        # SESSION SHUTDOWN
        #
        # Flush all remaining spans and metrics
        # before the Python process exits.
        # =========================================

        shutdown_telemetry()

        print()
        print(
            "OS Agent session ended."
        )


if __name__ == "__main__":
    main()