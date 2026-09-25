import re
from typing import Any

from app.agent.tools import (
    check_account_status,
    check_refund_eligibility,
)
from app.llm.base import LLMProvider


class TicketAgent:
    """
    Simple ReAct-style support agent.

    The agent:
    1. Inspects the ticket.
    2. Decides whether a tool is needed.
    3. Executes the selected tool when appropriate.
    4. Produces a final customer response.
    """

    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider

    def _extract_customer_id(
        self,
        text: str,
    ) -> str | None:
        match = re.search(
            r"\bCUST\d{3}\b",
            text.upper(),
        )

        return match.group(0) if match else None

    def _extract_order_id(
        self,
        text: str,
    ) -> str | None:
        match = re.search(
            r"\bORD\d{3}\b",
            text.upper(),
        )

        return match.group(0) if match else None

    def _choose_action(
        self,
        category: str,
        urgency_level: str,
        ticket_text: str,
    ) -> str:

        text_lower = ticket_text.lower()

        if urgency_level == "critical":
            return "human_escalation"

        if category == "account":
            if self._extract_customer_id(ticket_text):
                return "check_account_status"

            return "human_escalation"

        if category == "billing":
            if "refund" in text_lower and self._extract_order_id(ticket_text):
                return "check_refund_eligibility"

            if urgency_level == "high":
                return "human_escalation"

        return "direct_answer"

    def _execute_tool(
        self,
        action: str,
        ticket_text: str,
    ) -> dict[str, Any] | None:

        if action == "check_account_status":
            customer_id = self._extract_customer_id(ticket_text)

            return check_account_status(customer_id)

        if action == "check_refund_eligibility":
            order_id = self._extract_order_id(ticket_text)

            return check_refund_eligibility(order_id)

        return None

    def run(
        self,
        subject: str,
        body: str,
        category: str,
        urgency: dict,
        retrieved_context: list[dict],
        system_prompt: str,
    ) -> dict[str, Any]:

        ticket_text = f"{subject}\n{body}"

        # Step 1: Decide what action the agent should take
        action = self._choose_action(
            category=category,
            urgency_level=urgency["level"],
            ticket_text=ticket_text,
        )

        tool_result = None
        tool_calls = []

        # Step 2: Execute tool if required
        if action in {
            "check_account_status",
            "check_refund_eligibility",
        }:
            tool_result = self._execute_tool(
                action,
                ticket_text,
            )

            tool_calls.append(
                {
                    "tool": action,
                    "result": tool_result,
                }
            )

        # Step 3: Build retrieved knowledge context
        context_text = "\n\n".join(
            [
                (f"Source: {item['source']}\n" f"{item['content']}")
                for item in retrieved_context
            ]
        )

        # Step 4: Generate response or escalate
        if action == "human_escalation":

            final_response = (
                "This issue requires review by a human "
                "support agent. Your ticket has been "
                "marked for escalation."
            )

        else:

            user_prompt = f"""
Ticket:
Subject: {subject}
Body: {body}

Category: {category}
Urgency: {urgency["level"]}

Relevant knowledge:
{context_text}

Tool result:
{tool_result}

Action: {action}

Write a concise customer-facing response using only the relevant knowledge and tool result.
""".strip()

            final_response = self.llm_provider.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )

        # Step 5: Build reasoning trace
        reasoning_trace = [
            f"Classified ticket as '{category}'.",
            (f"Urgency level is " f"'{urgency['level']}'."),
            f"Selected action '{action}'.",
        ]

        if tool_result is not None:
            reasoning_trace.append("Executed the selected verification tool.")

        if action == "human_escalation":
            reasoning_trace.append(
                "Escalation selected because the " "ticket requires human intervention."
            )

        # Step 6: Return agent result
        return {
            "action": action,
            "tool_calls": tool_calls,
            "reasoning_trace": reasoning_trace,
            "final_response": final_response,
        }
