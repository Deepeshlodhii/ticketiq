from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    WorkflowStatusResponse,
)
from app.workflow.engine import WorkflowEngine

router = APIRouter()


@router.get(
    "/ticket/{transaction_id}/status",
    response_model=WorkflowStatusResponse,
)
async def get_ticket_status(
    transaction_id: str,
):
    engine = WorkflowEngine(transaction_id)

    stages = engine.get_all_statuses()

    if not stages:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found",
        )

    return {
        "transaction_id": transaction_id,
        "stages": stages,
    }
