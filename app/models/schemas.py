from typing import Any

from pydantic import BaseModel, Field


class TicketRequest(BaseModel):
    subject: str = Field(min_length=1)
    body: str = Field(min_length=1)
    tier: str = Field(
        default="standard",
        pattern="^(basic|standard|premium)$",
    )


class FeedbackRequest(BaseModel):
    transaction_id: str
    feedback: int = Field(
        ge=0,
        le=1,
    )


class TicketResponse(BaseModel):
    transaction_id: str

    category: dict[str, Any]

    sentiment: dict[str, Any]

    urgency: dict[str, Any]

    retrieved_snippets: list[dict[str, Any]]

    agent_action: str

    tool_calls: list[dict[str, Any]]

    reasoning_trace: list[str]

    final_response: str

    pipeline_config: dict[str, Any]

    latency_seconds: float


class FeedbackResponse(BaseModel):
    transaction_id: str
    feedback: int
    reward: float
    action: str


class StageStatus(BaseModel):
    stage_name: str
    status: str
    output: Any = None
    error: str | None = None
    updated_at: str | None = None


class WorkflowStatusResponse(BaseModel):
    transaction_id: str
    stages: list[StageStatus]
