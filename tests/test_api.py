from fastapi.testclient import TestClient

from app.api import tickets
from app.main import app


client = TestClient(app)


def test_create_ticket_api_with_mocked_pipeline(monkeypatch):
    async def mock_process_ticket(subject, body, tier):
        return {
            "transaction_id": "api-test-001",
            "category": {"label": "billing"},
            "sentiment": {"billing": {"compound": -0.5}},
            "urgency": {"score": 0.7, "level": "high"},
            "retrieved_snippets": [
                {
                    "source": "billing.md",
                    "text": "Billing support information.",
                }
            ],
            "agent_action": "direct_answer",
            "tool_calls": [],
            "reasoning_trace": ["Billing issue identified."],
            "final_response": "Please check your billing details.",
            "pipeline_config": {
                "name": "config_a",
                "top_k": 3,
            },
            "latency_seconds": 0.01,
        }

    monkeypatch.setattr(
        tickets.pipeline,
        "process_ticket",
        mock_process_ticket,
    )

    response = client.post(
        "/ticket",
        json={
            "subject": "Billing issue",
            "body": "I have a problem with my payment.",
            "tier": "standard",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["transaction_id"] == "api-test-001"
    assert data["category"]["label"] == "billing"
    assert data["agent_action"] == "direct_answer"
    assert data["pipeline_config"]["name"] == "config_a"
