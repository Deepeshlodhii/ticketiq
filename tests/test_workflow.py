import asyncio

from app.storage import get_connection, init_db
from app.workflow.engine import WorkflowEngine


def test_workflow_dependencies_and_rerun():
    init_db()

    transaction_id = "workflow-test-002"

    # Clean previous test data so the test is repeatable.
    conn = get_connection()
    conn.execute(
        "DELETE FROM stages WHERE transaction_id = ?",
        (transaction_id,),
    )
    conn.commit()
    conn.close()

    engine = WorkflowEngine(transaction_id)

    execution = []

    async def stage_a(context):
        execution.append("A")
        return {"value": 10}

    async def stage_b(context):
        execution.append("B")
        return {"value": context["a"]["value"] + 5}

    async def run():
        context = {}

        result_a = await engine.run_stage(
            stage_name="a",
            dependencies=[],
            function=stage_a,
            context=context,
        )

        context["a"] = result_a

        result_b = await engine.run_stage(
            stage_name="b",
            dependencies=["a"],
            function=stage_b,
            context=context,
        )

        return result_a, result_b

    result_a, result_b = asyncio.run(run())

    assert result_a == {"value": 10}
    assert result_b == {"value": 15}

    # Both stages should execute once.
    assert execution == ["A", "B"]

    # Completed stage should be loaded from SQLite
    # instead of executing again.
    result_a_again = asyncio.run(
        engine.run_stage(
            stage_name="a",
            dependencies=[],
            function=stage_a,
            context={"a": result_a},
        )
    )

    assert result_a_again == {"value": 10}

    # Stage A should NOT have executed again.
    assert execution == ["A", "B"]

    # Verify persisted status.
    status_a = engine.get_stage_status("a")
    status_b = engine.get_stage_status("b")

    assert status_a["status"] == "completed"
    assert status_b["status"] == "completed"
