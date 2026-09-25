from app.api.feedback import submit_feedback
from app.models.schemas import FeedbackRequest
from app.storage import get_connection, init_db


def test_feedback_updates_bandit():
    init_db()

    transaction_id = "test-feedback-001"

    conn = get_connection()

    conn.execute(
        """
        INSERT OR REPLACE INTO tickets (
            transaction_id,
            subject,
            body,
            tier
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            transaction_id,
            "Refund issue",
            "Refund not received for order ORD001",
            "premium",
        ),
    )

    conn.execute(
        """
        INSERT OR REPLACE INTO ticket_runs (
            transaction_id,
            bandit_state,
            bandit_action,
            latency_seconds
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            transaction_id,
            "billing|medium|premium",
            "config_a",
            2.0,
        ),
    )

    conn.commit()
    conn.close()

    request = FeedbackRequest(
        transaction_id=transaction_id,
        feedback=1,
    )

    # FastAPI endpoint functions can be tested directly.
    import asyncio

    result = asyncio.run(submit_feedback(request))

    assert result.transaction_id == transaction_id
    assert result.feedback == 1
    assert result.reward == 8.0
    assert result.action == "config_a"

    conn = get_connection()

    row = conn.execute(
        """
        SELECT feedback, reward
        FROM ticket_runs
        WHERE transaction_id = ?
        """,
        (transaction_id,),
    ).fetchone()

    conn.close()

    assert row == (1, 8.0)
