import json
import sqlite3

from datetime import datetime
from pathlib import Path

from .models import (
    Run,
    RuntimeEvent,
    Step,
)

from .status import (
    EventType,
    RunStatus,
    StepStatus,
)


class SQLiteRunStore:
    """
    Persistent storage for OS Agent runtime state.

    Runtime v0 stores:

    - Runs
    - Steps
    - Runtime events

    SQLite is intentionally used as the first
    persistence backend so execution semantics can
    mature before introducing distributed storage.
    """

    def __init__(
        self,
        database_path: str = "data/os_agent.db",
    ):
        self.database_path = Path(
            database_path
        )

        self.database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._initialize_schema()

    # =============================================
    # CONNECTION
    # =============================================

    def _connect(
        self,
    ) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self.database_path,
            timeout=30,
        )

        connection.row_factory = (
            sqlite3.Row
        )

        connection.execute(
            "PRAGMA foreign_keys = ON"
        )

        return connection

    # =============================================
    # SCHEMA
    # =============================================

    def _initialize_schema(
        self,
    ) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY,
                    goal TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    started_at TEXT,
                    completed_at TEXT,
                    current_step INTEGER NOT NULL DEFAULT 0,
                    outcome TEXT
                );

                CREATE TABLE IF NOT EXISTS steps (
                    step_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    number INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    completed_at TEXT,
                    proposed_action TEXT,
                    outcome TEXT,

                    FOREIGN KEY (run_id)
                        REFERENCES runs(run_id)
                        ON DELETE CASCADE,

                    UNIQUE (run_id, number)
                );

                CREATE TABLE IF NOT EXISTS events (
                    event_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    step_id TEXT,
                    event_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    data TEXT NOT NULL,

                    FOREIGN KEY (run_id)
                        REFERENCES runs(run_id)
                        ON DELETE CASCADE,

                    FOREIGN KEY (step_id)
                        REFERENCES steps(step_id)
                        ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS
                    idx_steps_run_number
                ON steps (
                    run_id,
                    number
                );

                CREATE INDEX IF NOT EXISTS
                    idx_events_run_timestamp
                ON events (
                    run_id,
                    timestamp
                );

                CREATE INDEX IF NOT EXISTS
                    idx_events_step
                ON events (
                    step_id
                );
                """
            )

    # =============================================
    # RUNS
    # =============================================

    def create_run(
        self,
        run: Run,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO runs (
                    run_id,
                    goal,
                    status,
                    created_at,
                    started_at,
                    completed_at,
                    current_step,
                    outcome
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run.run_id,
                    run.goal,
                    run.status.value,
                    run.created_at.isoformat(),
                    self._serialize_datetime(
                        run.started_at
                    ),
                    self._serialize_datetime(
                        run.completed_at
                    ),
                    run.current_step,
                    run.outcome,
                ),
            )

    def update_run(
        self,
        run: Run,
    ) -> None:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                UPDATE runs
                SET
                    goal = ?,
                    status = ?,
                    created_at = ?,
                    started_at = ?,
                    completed_at = ?,
                    current_step = ?,
                    outcome = ?
                WHERE run_id = ?
                """,
                (
                    run.goal,
                    run.status.value,
                    run.created_at.isoformat(),
                    self._serialize_datetime(
                        run.started_at
                    ),
                    self._serialize_datetime(
                        run.completed_at
                    ),
                    run.current_step,
                    run.outcome,
                    run.run_id,
                ),
            )

            if cursor.rowcount == 0:
                raise KeyError(
                    f"Run not found: {run.run_id}"
                )

    def get_run(
        self,
        run_id: str,
    ) -> Run | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM runs
                WHERE run_id = ?
                """,
                (
                    run_id,
                ),
            ).fetchone()

        if row is None:
            return None

        return self._row_to_run(
            row
        )

    # =============================================
    # STEPS
    # =============================================

    def create_step(
        self,
        step: Step,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO steps (
                    step_id,
                    run_id,
                    number,
                    status,
                    started_at,
                    completed_at,
                    proposed_action,
                    outcome
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    step.step_id,
                    step.run_id,
                    step.number,
                    step.status.value,
                    step.started_at.isoformat(),
                    self._serialize_datetime(
                        step.completed_at
                    ),
                    self._serialize_json(
                        step.proposed_action
                    ),
                    step.outcome,
                ),
            )

    def update_step(
        self,
        step: Step,
    ) -> None:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                UPDATE steps
                SET
                    run_id = ?,
                    number = ?,
                    status = ?,
                    started_at = ?,
                    completed_at = ?,
                    proposed_action = ?,
                    outcome = ?
                WHERE step_id = ?
                """,
                (
                    step.run_id,
                    step.number,
                    step.status.value,
                    step.started_at.isoformat(),
                    self._serialize_datetime(
                        step.completed_at
                    ),
                    self._serialize_json(
                        step.proposed_action
                    ),
                    step.outcome,
                    step.step_id,
                ),
            )

            if cursor.rowcount == 0:
                raise KeyError(
                    f"Step not found: {step.step_id}"
                )

    def get_step(
        self,
        step_id: str,
    ) -> Step | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM steps
                WHERE step_id = ?
                """,
                (
                    step_id,
                ),
            ).fetchone()

        if row is None:
            return None

        return self._row_to_step(
            row
        )

    def list_steps(
        self,
        run_id: str,
    ) -> list[Step]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM steps
                WHERE run_id = ?
                ORDER BY number ASC
                """,
                (
                    run_id,
                ),
            ).fetchall()

        return [
            self._row_to_step(row)
            for row in rows
        ]

    # =============================================
    # EVENTS
    # =============================================

    def append_event(
        self,
        event: RuntimeEvent,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO events (
                    event_id,
                    run_id,
                    step_id,
                    event_type,
                    timestamp,
                    data
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    event.event_id,
                    event.run_id,
                    event.step_id,
                    event.event_type.value,
                    event.timestamp.isoformat(),
                    self._serialize_json(
                        event.data
                    ),
                ),
            )

    def list_events(
        self,
        run_id: str,
        step_id: str | None = None,
    ) -> list[RuntimeEvent]:
        with self._connect() as connection:
            if step_id is None:
                rows = connection.execute(
                    """
                    SELECT *
                    FROM events
                    WHERE run_id = ?
                    ORDER BY timestamp ASC
                    """,
                    (
                        run_id,
                    ),
                ).fetchall()

            else:
                rows = connection.execute(
                    """
                    SELECT *
                    FROM events
                    WHERE
                        run_id = ?
                        AND step_id = ?
                    ORDER BY timestamp ASC
                    """,
                    (
                        run_id,
                        step_id,
                    ),
                ).fetchall()

        return [
            self._row_to_event(row)
            for row in rows
        ]

    # =============================================
    # SERIALIZATION
    # =============================================

    @staticmethod
    def _serialize_datetime(
        value: datetime | None,
    ) -> str | None:
        if value is None:
            return None

        return value.isoformat()

    @staticmethod
    def _deserialize_datetime(
        value: str | None,
    ) -> datetime | None:
        if value is None:
            return None

        return datetime.fromisoformat(
            value
        )

    @staticmethod
    def _serialize_json(
        value,
    ) -> str | None:
        if value is None:
            return None

        return json.dumps(
            value,
            ensure_ascii=False,
        )

    @staticmethod
    def _deserialize_json(
        value: str | None,
    ):
        if value is None:
            return None

        return json.loads(
            value
        )

    # =============================================
    # ROW CONVERSION
    # =============================================

    def _row_to_run(
        self,
        row: sqlite3.Row,
    ) -> Run:
        return Run(
            run_id=row["run_id"],
            goal=row["goal"],
            status=RunStatus(
                row["status"]
            ),
            created_at=datetime.fromisoformat(
                row["created_at"]
            ),
            started_at=self._deserialize_datetime(
                row["started_at"]
            ),
            completed_at=self._deserialize_datetime(
                row["completed_at"]
            ),
            current_step=row[
                "current_step"
            ],
            outcome=row["outcome"],
        )

    def _row_to_step(
        self,
        row: sqlite3.Row,
    ) -> Step:
        return Step(
            step_id=row["step_id"],
            run_id=row["run_id"],
            number=row["number"],
            status=StepStatus(
                row["status"]
            ),
            started_at=datetime.fromisoformat(
                row["started_at"]
            ),
            completed_at=self._deserialize_datetime(
                row["completed_at"]
            ),
            proposed_action=self._deserialize_json(
                row["proposed_action"]
            ),
            outcome=row["outcome"],
        )

    def _row_to_event(
        self,
        row: sqlite3.Row,
    ) -> RuntimeEvent:
        return RuntimeEvent(
            event_id=row["event_id"],
            run_id=row["run_id"],
            step_id=row["step_id"],
            event_type=EventType(
                row["event_type"]
            ),
            timestamp=datetime.fromisoformat(
                row["timestamp"]
            ),
            data=(
                self._deserialize_json(
                    row["data"]
                )
                or {}
            ),
        )