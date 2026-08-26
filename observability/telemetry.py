import os

from opentelemetry import (
    metrics,
    trace,
)

from opentelemetry.exporter.otlp.proto.http.metric_exporter import (
    OTLPMetricExporter,
)

from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    OTLPSpanExporter,
)

from opentelemetry.sdk.metrics import (
    MeterProvider,
)

from opentelemetry.sdk.metrics.export import (
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
    BatchSpanProcessor,
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

    # =============================================
    # RESOURCE
    # =============================================

    resource = Resource.create(
        {
            SERVICE_NAME: "os-agent",
        }
    )

    # =============================================
    # OTLP ENDPOINT
    #
    # Grafana OTEL-LGTM exposes OTLP/HTTP
    # on localhost:4318.
    # =============================================

    otlp_endpoint = os.getenv(
        "OTEL_EXPORTER_OTLP_ENDPOINT",
        "http://localhost:4318",
    ).rstrip("/")

    # =============================================
    # TRACING
    # =============================================

    span_exporter = OTLPSpanExporter(
        endpoint=(
            f"{otlp_endpoint}/v1/traces"
        ),
    )

    tracer_provider = TracerProvider(
        resource=resource,
    )

    tracer_provider.add_span_processor(
        BatchSpanProcessor(
            span_exporter
        )
    )

    trace.set_tracer_provider(
        tracer_provider
    )

    _tracer_provider = (
        tracer_provider
    )

    # =============================================
    # METRICS
    # =============================================

    metric_exporter = OTLPMetricExporter(
        endpoint=(
            f"{otlp_endpoint}/v1/metrics"
        ),
    )

    metric_reader = (
        PeriodicExportingMetricReader(
            metric_exporter,
            export_interval_millis=5000,
        )
    )

    meter_provider = MeterProvider(
        resource=resource,
        metric_readers=[
            metric_reader,
        ],
    )

    metrics.set_meter_provider(
        meter_provider
    )

    _meter_provider = (
        meter_provider
    )

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

    OS Agent currently runs as a short-lived CLI
    process, so explicit shutdown ensures traces
    and metrics are exported before Python exits.
    """

    global _tracer_provider
    global _meter_provider

    if _meter_provider is not None:
        _meter_provider.shutdown()

    if _tracer_provider is not None:
        _tracer_provider.shutdown()