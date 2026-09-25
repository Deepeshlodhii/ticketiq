import time
import uuid

from app.agent.agent import TicketAgent
from app.agent.prompts import CONFIGS
from app.config import DATABASE_PATH
from app.llm.ollama_provider import OllamaProvider
from app.ml.classifier import TicketClassifier, load_dataset
from app.rag.retriever import KnowledgeBaseRetriever
from app.rl.bandit import ContextualBandit
from app.sentiment.aspect_sentiment import AspectSentimentAnalyzer
from app.storage import get_connection
from app.urgency import calculate_urgency
from app.workflow.engine import WorkflowEngine


class TicketPipeline:
    """
    Main TicketIQ processing pipeline.

    Independent classification and sentiment stages run concurrently.
    Later stages depend on their outputs.
    """

    def __init__(self):
        # Train classifier once.
        self.classifier = TicketClassifier()

        texts, labels = load_dataset("data/tickets.csv")

        self.classifier.train(
            texts,
            labels,
        )

        # Initialize reusable components once.
        self.sentiment_analyzer = AspectSentimentAnalyzer()

        self.retriever = KnowledgeBaseRetriever()

        self.bandit = ContextualBandit()

        self.llm_provider = OllamaProvider()

        self.agent = TicketAgent(self.llm_provider)

    async def process_ticket(self, subject: str, body: str, tier: str):
        pipeline_start = time.perf_counter()

        transaction_id = str(uuid.uuid4())

        conn = get_connection()

        conn.execute(
            """
            INSERT INTO tickets (
                transaction_id,
                subject,
                body,
                tier
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                transaction_id,
                subject,
                body,
                tier,
            ),
        )

        conn.commit()
        conn.close()

        print(f"[DB] Saved ticket {transaction_id} to {DATABASE_PATH}")

        engine = WorkflowEngine(transaction_id)

        context = {
            "subject": subject,
            "body": body,
            "tier": tier,
        }

        # --------------------------------------------------
        # Stage 1A: Classification
        # --------------------------------------------------

        async def classification_stage(ctx):
            text = f"{ctx['subject']}\n" f"{ctx['body']}"

            category, confidence = self.classifier.predict(text)

            return {
                "category": category,
                "confidence": round(
                    confidence,
                    4,
                ),
            }

        # --------------------------------------------------
        # Stage 1B: Sentiment
        # --------------------------------------------------

        async def sentiment_stage(ctx):
            text = f"{ctx['subject']}\n" f"{ctx['body']}"

            return self.sentiment_analyzer.analyze(text)

        # Classification and sentiment are independent.
        classification_result, sentiment_result = await engine.run_parallel(
            [
                {
                    "name": "classification",
                    "dependencies": [],
                    "function": classification_stage,
                },
                {
                    "name": "sentiment",
                    "dependencies": [],
                    "function": sentiment_stage,
                },
            ],
            context,
        )

        context["classification"] = classification_result

        context["sentiment"] = sentiment_result

        # --------------------------------------------------
        # Stage 2: Urgency
        # --------------------------------------------------

        async def urgency_stage(ctx):
            return calculate_urgency(
                category=ctx["classification"]["category"],
                sentiment_data=ctx["sentiment"],
                tier=ctx["tier"],
            )

        urgency_result = await engine.run_stage(
            stage_name="urgency",
            dependencies=[
                "classification",
                "sentiment",
            ],
            function=urgency_stage,
            context=context,
        )

        context["urgency"] = urgency_result

        # --------------------------------------------------
        # Stage 3: Bandit configuration selection
        # --------------------------------------------------

        async def bandit_stage(ctx):
            return self.bandit.select_action(
                category=ctx["classification"]["category"],
                urgency_score=ctx["urgency"]["score"],
                tier=ctx["tier"],
            )

        bandit_result = await engine.run_stage(
            stage_name="bandit_selection",
            dependencies=[
                "urgency",
            ],
            function=bandit_stage,
            context=context,
        )

        context["bandit"] = bandit_result

        selected_action = bandit_result["action"]

        selected_config = CONFIGS[selected_action]

        context["config"] = selected_config

        # Save the contextual bandit state
        bandit_state = bandit_result["state"]
        context["bandit_state"] = bandit_state
        context["selected_action"] = selected_action

        # --------------------------------------------------
        # Stage 4: RAG retrieval
        # --------------------------------------------------

        async def rag_stage(ctx):
            query = f"{ctx['subject']}\n" f"{ctx['body']}"

            return self.retriever.retrieve(
                query=query,
                top_k=ctx["config"]["top_k"],
            )

        rag_result = await engine.run_stage(
            stage_name="rag",
            dependencies=[
                "bandit_selection",
            ],
            function=rag_stage,
            context=context,
        )

        context["rag"] = rag_result

        # --------------------------------------------------
        # Stage 5: Agent
        # --------------------------------------------------

        async def agent_stage(ctx):
            return self.agent.run(
                subject=ctx["subject"],
                body=ctx["body"],
                category=ctx["classification"]["category"],
                urgency=ctx["urgency"],
                retrieved_context=ctx["rag"],
                system_prompt=ctx["config"]["system_prompt"],
            )

        agent_result = await engine.run_stage(
            stage_name="agent",
            dependencies=[
                "rag",
            ],
            function=agent_stage,
            context=context,
        )

        latency = time.perf_counter() - pipeline_start

        context["agent"] = agent_result

        # --------------------------------------------------
        # Final result
        # --------------------------------------------------

        conn = get_connection()

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
                context["bandit_state"],
                context["selected_action"],
                latency,
            ),
        )

        conn.commit()
        conn.close()

        return {
            "transaction_id": transaction_id,
            "category": context["classification"],
            "sentiment": context["sentiment"],
            "urgency": context["urgency"],
            "retrieved_snippets": context["rag"],
            "agent_action": agent_result["action"],
            "tool_calls": agent_result["tool_calls"],
            "reasoning_trace": agent_result["reasoning_trace"],
            "final_response": agent_result["final_response"],
            "pipeline_config": {
                "model": self.llm_provider.model,
                "prompt_config": selected_action,
                "top_k": selected_config["top_k"],
            },
            "latency_seconds": round(
                latency,
                4,
            ),
        }
