from unittest.mock import Mock

from app.agent.agent import TicketAgent


def create_agent():
    mock_llm = Mock()

    mock_llm.generate.return_value = "I can help you with this issue."

    return TicketAgent(mock_llm)


def test_account_tool_selected():
    agent = create_agent()

    result = agent.run(
        subject="Cannot access my account",
        body=("My account is locked. " "Customer ID is CUST002."),
        category="account",
        urgency={
            "score": 0.6,
            "level": "high",
        },
        retrieved_context=[],
        system_prompt="Test prompt",
    )

    assert result["action"] == "check_account_status"

    assert result["tool_calls"][0]["tool"] == "check_account_status"


def test_refund_tool_selected():
    agent = create_agent()

    result = agent.run(
        subject="I need a refund",
        body=("Please check my refund. " "Order ID is ORD003."),
        category="billing",
        urgency={
            "score": 0.4,
            "level": "medium",
        },
        retrieved_context=[],
        system_prompt="Test prompt",
    )

    assert result["action"] == "check_refund_eligibility"


def test_critical_ticket_escalated():
    agent = create_agent()

    result = agent.run(
        subject="System failure",
        body="Everything is completely down.",
        category="technical",
        urgency={
            "score": 0.95,
            "level": "critical",
        },
        retrieved_context=[],
        system_prompt="Test prompt",
    )

    assert result["action"] == "human_escalation"


def test_simple_ticket_gets_direct_answer():
    agent = create_agent()

    result = agent.run(
        subject="How do I use this?",
        body="I need some general information.",
        category="feature_request",
        urgency={
            "score": 0.2,
            "level": "low",
        },
        retrieved_context=[],
        system_prompt="Test prompt",
    )

    assert result["action"] == "direct_answer"
