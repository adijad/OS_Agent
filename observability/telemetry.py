from opentelemetry import trace

from opentelemetry.sdk.resources import (
    Resource,
    SERVICE_NAME,
)

from opentelemetry.sdk.trace import (
    TracerProvider,
)

from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)


_configured = False


def configure_telemetry():
    """
    Configure OpenTelemetry for OS Agent.

    V1 exports traces to the console.

    Later we can replace or supplement this
    with an OTLP exporter without changing
    the agent instrumentation.
    """

    global _configured

    if _configured:
        return

    resource = Resource.create(
        {
            SERVICE_NAME: "os-agent",
        }
    )

    provider = TracerProvider(
        resource=resource
    )

    provider.add_span_processor(
        BatchSpanProcessor(
            ConsoleSpanExporter()
        )
    )

    trace.set_tracer_provider(
        provider
    )

    _configured = True


def get_tracer(
    name: str,
):
    return trace.get_tracer(
        name
    )