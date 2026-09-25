from fastapi import APIRouter

from app.models.schemas import (
    TicketRequest,
    TicketResponse,
)
from app.workflow.pipeline import TicketPipeline

router = APIRouter()

pipeline = TicketPipeline()


@router.post(
    "/ticket",
    response_model=TicketResponse,
)
async def create_ticket(
    ticket: TicketRequest,
):
    result = await pipeline.process_ticket(
        subject=ticket.subject,
        body=ticket.body,
        tier=ticket.tier,
    )

    return result
