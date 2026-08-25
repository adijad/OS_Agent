from opentelemetry import (
    metrics,
    trace,
)

from opentelemetry.sdk.metrics import (
    MeterProvider,
)

from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    PeriodicExportingMetricReader,
)

from opentelemetry.sdk.resources import (
    Resource,
    SERVICE_NAME,
)

from opentelemetry.sdk.trace import (
    TracerProvider,
)

from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)


_configured = False

_tracer_provider = None
_meter_provider = None


def configure_telemetry():
    global _configured
    global _tracer_provider
    global _meter_provider

    if _configured:
        return

    resource = Resource.create(
        {
            SERVICE_NAME: "os-agent",
        }
    )

    # =============================================
    # TRACING
    # =============================================

    tracer_provider = TracerProvider(
        resource=resource
    )

    tracer_provider.add_span_processor(
        SimpleSpanProcessor(
            ConsoleSpanExporter()
        )
    )

    trace.set_tracer_provider(
        tracer_provider
    )

    _tracer_provider = tracer_provider

    # =============================================
    # METRICS
    # =============================================

    metric_reader = (
        PeriodicExportingMetricReader(
            ConsoleMetricExporter(),
            export_interval_millis=5000,
        )
    )

    meter_provider = MeterProvider(
        resource=resource,
        metric_readers=[
            metric_reader
        ],
    )

    metrics.set_meter_provider(
        meter_provider
    )

    _meter_provider = meter_provider

    _configured = True


def get_tracer(
    name: str,
):
    return trace.get_tracer(
        name
    )


def get_meter(
    name: str,
):
    return metrics.get_meter(
        name
    )


def shutdown_telemetry():
    """
    Flush and shut down telemetry providers.

    This is especially important for metrics
    because OS Agent currently runs as a
    short-lived CLI process.
    """

    global _tracer_provider
    global _meter_provider

    if _meter_provider is not None:
        _meter_provider.shutdown()

    if _tracer_provider is not None:
        _tracer_provider.shutdown()