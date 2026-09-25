from fastapi import APIRouter, HTTPException

from app.models.schemas import FeedbackRequest, FeedbackResponse
from app.rl.bandit import ContextualBandit
from app.storage import get_connection

router = APIRouter()

bandit = ContextualBandit()


@router.post(
    "/feedback",
    response_model=FeedbackResponse,
)
async def submit_feedback(
    feedback: FeedbackRequest,
):
    conn = get_connection()

    ticket_run = conn.execute(
        """
        SELECT
            transaction_id,
            bandit_state,
            bandit_action,
            latency_seconds
        FROM ticket_runs
        WHERE transaction_id = ?
        """,
        (feedback.transaction_id,),
    ).fetchone()

    if ticket_run is None:
        conn.close()

        raise HTTPException(
            status_code=404,
            detail="Transaction ID not found.",
        )

    (
        transaction_id,
        bandit_state,
        bandit_action,
        latency_seconds,
    ) = ticket_run

    conn.close()

    # Update the contextual bandit.
    # The bandit calculates:
    # reward = (feedback * 10) - latency_seconds
    bandit_result = bandit.update(
        state=bandit_state,
        action=bandit_action,
        feedback=feedback.feedback,
        latency_seconds=latency_seconds,
    )

    reward = bandit_result["reward"]

    # Persist feedback and calculated reward.
    conn = get_connection()

    conn.execute(
        """
        INSERT INTO feedback (
            transaction_id,
            feedback
        )
        VALUES (?, ?)
        """,
        (
            transaction_id,
            feedback.feedback,
        ),
    )

    conn.execute(
        """
        UPDATE ticket_runs
        SET
            feedback = ?,
            reward = ?
        WHERE transaction_id = ?
        """,
        (
            feedback.feedback,
            reward,
            transaction_id,
        ),
    )

    conn.commit()
    conn.close()

    return FeedbackResponse(
        transaction_id=transaction_id,
        feedback=feedback.feedback,
        reward=reward,
        action=bandit_action,
    )
