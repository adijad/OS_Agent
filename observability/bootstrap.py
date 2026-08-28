import shutil
import socket
import subprocess
import time

from pathlib import Path

from urllib.request import (
    urlopen,
)


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

COMPOSE_FILE = (
    PROJECT_ROOT
    / "docker-compose-observability.yml"
)

OTLP_HOST = "127.0.0.1"
OTLP_PORT = 4318

GRAFANA_HEALTH_URL = (
    "http://localhost:3000/api/health"
)


# =============================================
# OTLP CHECK
# =============================================


def is_otlp_available() -> bool:
    """
    Check whether the OTLP HTTP endpoint
    is accepting connections.
    """

    try:
        with socket.create_connection(
            (
                OTLP_HOST,
                OTLP_PORT,
            ),
            timeout=1.0,
        ):
            return True

    except OSError:
        return False


# =============================================
# GRAFANA CHECK
# =============================================


def is_grafana_available() -> bool:
    """
    Check whether Grafana has finished
    starting.
    """

    try:
        with urlopen(
            GRAFANA_HEALTH_URL,
            timeout=2.0,
        ) as response:
            return (
                200
                <= response.status
                < 300
            )

    except Exception:
        return False


# =============================================
# FULL OBSERVABILITY CHECK
# =============================================


def is_observability_available() -> bool:
    return (
        is_otlp_available()
        and is_grafana_available()
    )


# =============================================
# DOCKER CHECK
# =============================================


def is_docker_available() -> bool:
    """
    Check both:

    - Docker CLI exists
    - Docker daemon is reachable
    """

    if shutil.which(
        "docker"
    ) is None:
        return False

    result = subprocess.run(
        [
            "docker",
            "info",
        ],
        cwd=PROJECT_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )

    return (
        result.returncode
        == 0
    )


# =============================================
# START STACK
# =============================================


def start_observability() -> None:
    """
    Start the local OpenTelemetry / Grafana
    observability stack.
    """

    result = subprocess.run(
        [
            "docker",
            "compose",
            "-f",
            str(COMPOSE_FILE),
            "up",
            "-d",
        ],
        cwd=PROJECT_ROOT,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "Docker Compose failed to start "
            "the observability stack."
        )


# =============================================
# ENSURE OBSERVABILITY
# =============================================


def ensure_observability(
    timeout_seconds: int = 30,
) -> None:
    """
    Ensure the OS Agent observability stack
    is available before an agent run begins.

    If it is already available:
        continue immediately.

    If Docker is available but the stack is
    stopped:
        start it automatically.

    If Docker itself is unavailable:
        abort the run.
    """

    if is_observability_available():
        print(
            "✅ Observability ready"
        )
        return

    print(
        "Observability stack is not running."
    )

    # =========================================
    # VERIFY DOCKER
    # =========================================

    if not is_docker_available():
        raise RuntimeError(
            "Docker is not available. "
            "Start Docker Desktop before "
            "running OS Agent."
        )

    # =========================================
    # START STACK
    # =========================================

    print(
        "Starting observability stack..."
    )

    start_observability()

    # =========================================
    # WAIT FOR SERVICES
    # =========================================

    deadline = (
        time.monotonic()
        + timeout_seconds
    )

    while (
        time.monotonic()
        < deadline
    ):
        if is_observability_available():
            print(
                "✅ Observability ready"
            )
            return

        time.sleep(
            1
        )

    raise RuntimeError(
        "Observability stack did not become "
        f"ready within {timeout_seconds} seconds."
    )