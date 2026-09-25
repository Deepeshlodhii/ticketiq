import asyncio
import json
from typing import Any

from app.storage import get_connection


class WorkflowEngine:
    """
    Lightweight dependency-aware workflow engine.

    Each stage has:
        - a name
        - dependencies
        - a function

    Stage state is persisted in SQLite.
    """

    def __init__(self, transaction_id: str):
        self.transaction_id = transaction_id

    def save_stage(
        self,
        stage_name: str,
        status: str,
        output: Any = None,
        error: str | None = None,
    ):
        conn = get_connection()

        conn.execute(
            """
            INSERT INTO stages
            (
                transaction_id,
                stage_name,
                status,
                output,
                error
            )
            VALUES (?, ?, ?, ?, ?)

            ON CONFLICT(
                transaction_id,
                stage_name
            )
            DO UPDATE SET
                status = excluded.status,
                output = excluded.output,
                error = excluded.error,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                self.transaction_id,
                stage_name,
                status,
                json.dumps(output) if output is not None else None,
                error,
            ),
        )

        conn.commit()
        conn.close()

    def get_stage_status(
        self,
        stage_name: str,
    ) -> dict | None:

        conn = get_connection()

        row = conn.execute(
            """
            SELECT
                stage_name,
                status,
                output,
                error,
                updated_at
            FROM stages
            WHERE transaction_id = ?
              AND stage_name = ?
            """,
            (
                self.transaction_id,
                stage_name,
            ),
        ).fetchone()

        conn.close()

        if row is None:
            return None

        return {
            "stage_name": row[0],
            "status": row[1],
            "output": (json.loads(row[2]) if row[2] else None),
            "error": row[3],
            "updated_at": row[4],
        }

    def get_all_statuses(self) -> list[dict]:

        conn = get_connection()

        rows = conn.execute(
            """
            SELECT
                stage_name,
                status,
                output,
                error,
                updated_at
            FROM stages
            WHERE transaction_id = ?
            ORDER BY updated_at
            """,
            (self.transaction_id,),
        ).fetchall()

        conn.close()

        return [
            {
                "stage_name": row[0],
                "status": row[1],
                "output": (json.loads(row[2]) if row[2] else None),
                "error": row[3],
                "updated_at": row[4],
            }
            for row in rows
        ]

    async def run_stage(
        self,
        stage_name: str,
        dependencies: list[str],
        function,
        context: dict[str, Any],
    ):

        # Check whether this stage already succeeded.
        existing = self.get_stage_status(stage_name)

        if existing and existing["status"] == "completed":
            return existing["output"]

        # Verify dependencies.
        for dependency in dependencies:
            dependency_status = self.get_stage_status(dependency)

            if dependency_status is None or dependency_status["status"] != "completed":
                raise RuntimeError(
                    f"Dependency '{dependency}' "
                    f"for stage '{stage_name}' "
                    f"is not completed."
                )

        self.save_stage(
            stage_name,
            "running",
        )

        try:
            result = await function(context)

            self.save_stage(
                stage_name,
                "completed",
                output=result,
            )

            return result

        except Exception as exc:
            self.save_stage(
                stage_name,
                "failed",
                error=str(exc),
            )

            raise

    async def run_parallel(
        self,
        stages,
        context: dict[str, Any],
    ):
        """
        Run independent stages concurrently.
        """

        tasks = []

        for stage in stages:
            tasks.append(
                self.run_stage(
                    stage_name=stage["name"],
                    dependencies=stage["dependencies"],
                    function=stage["function"],
                    context=context,
                )
            )

        return await asyncio.gather(*tasks)
