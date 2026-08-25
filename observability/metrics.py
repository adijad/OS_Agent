from observability.telemetry import get_meter


class AgentMetrics:
    def __init__(self):
        meter = get_meter(
            "os_agent.metrics"
        )

        # =============================================
        # RUN METRICS
        # =============================================

        self.runs = meter.create_counter(
            "os_agent.runs",
            description=(
                "Number of OS Agent runs."
            ),
        )

        self.run_duration = (
            meter.create_histogram(
                "os_agent.run.duration",
                unit="ms",
                description=(
                    "End-to-end OS Agent "
                    "run duration."
                ),
            )
        )

        self.run_steps = (
            meter.create_histogram(
                "os_agent.run.steps",
                description=(
                    "Number of steps in "
                    "an OS Agent run."
                ),
            )
        )

        # =============================================
        # MODEL METRICS
        # =============================================

        self.model_calls = (
            meter.create_counter(
                "os_agent.model.calls",
                description=(
                    "Number of model calls."
                ),
            )
        )

        self.model_duration = (
            meter.create_histogram(
                "os_agent.model.duration",
                unit="ms",
                description=(
                    "Model call latency."
                ),
            )
        )

        self.input_tokens = (
            meter.create_counter(
                "os_agent.tokens.input",
                description=(
                    "Model input tokens."
                ),
            )
        )

        self.output_tokens = (
            meter.create_counter(
                "os_agent.tokens.output",
                description=(
                    "Model output tokens."
                ),
            )
        )

        self.total_tokens = (
            meter.create_counter(
                "os_agent.tokens.total",
                description=(
                    "Total model tokens."
                ),
            )
        )

        # =============================================
        # OBSERVATION METRICS
        # =============================================

        self.observe_duration = (
            meter.create_histogram(
                "os_agent.observe.duration",
                unit="ms",
                description=(
                    "Computer observation latency."
                ),
            )
        )

        # =============================================
        # EXECUTOR METRICS
        # =============================================

        self.actions = (
            meter.create_counter(
                "os_agent.actions",
                description=(
                    "Number of computer actions."
                ),
            )
        )

        self.executor_duration = (
            meter.create_histogram(
                "os_agent.executor.duration",
                unit="ms",
                description=(
                    "Computer action execution "
                    "latency."
                ),
            )
        )

    # =============================================
    # RECORD MODEL CALL
    # =============================================

    def record_model_call(
        self,
        *,
        provider: str,
        model: str,
        latency_ms: float,
        input_tokens: int,
        output_tokens: int,
        total_tokens: int,
    ):
        attributes = {
            "provider": provider,
            "model": model,
        }

        self.model_calls.add(
            1,
            attributes,
        )

        self.model_duration.record(
            latency_ms,
            attributes,
        )

        self.input_tokens.add(
            input_tokens,
            attributes,
        )

        self.output_tokens.add(
            output_tokens,
            attributes,
        )

        self.total_tokens.add(
            total_tokens,
            attributes,
        )

    # =============================================
    # RECORD OBSERVATION
    # =============================================

    def record_observation(
        self,
        latency_ms: float,
    ):
        self.observe_duration.record(
            latency_ms
        )

    # =============================================
    # RECORD EXECUTOR ACTION
    # =============================================

    def record_action(
        self,
        *,
        action_type: str,
        status: str,
        latency_ms: float,
    ):
        attributes = {
            "action_type": action_type,
            "status": status,
        }

        self.actions.add(
            1,
            attributes,
        )

        self.executor_duration.record(
            latency_ms,
            attributes,
        )

    # =============================================
    # RECORD COMPLETED RUN
    # =============================================

    def record_run(
        self,
        *,
        provider: str,
        model: str,
        status: str,
        duration_ms: float,
        steps: int,
    ):
        attributes = {
            "provider": provider,
            "model": model,
            "status": status,
        }

        self.runs.add(
            1,
            attributes,
        )

        self.run_duration.record(
            duration_ms,
            attributes,
        )

        self.run_steps.record(
            steps,
            attributes,
        )