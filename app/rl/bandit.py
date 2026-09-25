import random

from app.config import EPSILON, REWARD_SCALE
from app.storage import get_connection

ACTIONS = {
    0: "config_a",
    1: "config_b",
}


class ContextualBandit:
    """
    Epsilon-greedy contextual bandit.

    Context:
        category
        urgency bucket
        customer tier

    Actions:
        config_a
        config_b

    Reward:
        (feedback * 10) - latency_seconds
    """

    def __init__(
        self,
        epsilon: float = EPSILON,
    ):
        self.epsilon = epsilon

        self._initialize_table()

    def _initialize_table(self):
        conn = get_connection()

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS bandit_stats (
                state TEXT,
                action TEXT,
                total_reward REAL DEFAULT 0,
                count INTEGER DEFAULT 0,
                PRIMARY KEY (state, action)
            )
            """
        )

        conn.commit()
        conn.close()

    @staticmethod
    def build_state(
        category: str,
        urgency_score: float,
        tier: str,
    ) -> str:

        if urgency_score >= 0.75:
            urgency_bucket = "critical"
        elif urgency_score >= 0.50:
            urgency_bucket = "high"
        elif urgency_score >= 0.25:
            urgency_bucket = "medium"
        else:
            urgency_bucket = "low"

        return f"{category}|" f"{urgency_bucket}|" f"{tier.lower()}"

    def _get_stats(
        self,
        state: str,
    ) -> dict[str, tuple[float, int]]:

        conn = get_connection()

        rows = conn.execute(
            """
            SELECT action, total_reward, count
            FROM bandit_stats
            WHERE state = ?
            """,
            (state,),
        ).fetchall()

        conn.close()

        stats = {action: (0.0, 0) for action in ACTIONS.values()}

        for action, total_reward, count in rows:
            stats[action] = (
                float(total_reward),
                int(count),
            )

        return stats

    def _ensure_state(
        self,
        state: str,
    ):
        conn = get_connection()

        for action in ACTIONS.values():
            conn.execute(
                """
                INSERT OR IGNORE INTO bandit_stats
                (state, action, total_reward, count)
                VALUES (?, ?, 0, 0)
                """,
                (state, action),
            )

        conn.commit()
        conn.close()

    def select_action(
        self,
        category: str,
        urgency_score: float,
        tier: str,
    ) -> dict:

        state = self.build_state(
            category,
            urgency_score,
            tier,
        )

        self._ensure_state(state)

        stats = self._get_stats(state)

        # Exploration
        if random.random() < self.epsilon:
            action = random.choice(list(ACTIONS.values()))

            selection_type = "exploration"

        # Exploitation
        else:
            action = max(
                ACTIONS.values(),
                key=lambda item: (
                    stats[item][0] / stats[item][1] if stats[item][1] > 0 else 0.0
                ),
            )

            selection_type = "exploitation"

        return {
            "state": state,
            "action": action,
            "selection_type": selection_type,
            "stats": {
                name: {
                    "total_reward": reward,
                    "count": count,
                    "average_reward": (reward / count if count > 0 else 0.0),
                }
                for name, (reward, count) in stats.items()
            },
        }

    def update(
        self,
        state: str,
        action: str,
        feedback: int,
        latency_seconds: float,
    ) -> dict:

        if action not in ACTIONS.values():
            raise ValueError(f"Unknown action: {action}")

        if feedback not in (0, 1):
            raise ValueError("Feedback must be either 0 or 1.")

        reward = feedback * REWARD_SCALE - latency_seconds

        conn = get_connection()

        conn.execute(
            """
            INSERT INTO bandit_stats
            (state, action, total_reward, count)
            VALUES (?, ?, ?, 1)

            ON CONFLICT(state, action)
            DO UPDATE SET
                total_reward =
                    total_reward + excluded.total_reward,
                count =
                    count + 1
            """,
            (
                state,
                action,
                reward,
            ),
        )

        conn.commit()
        conn.close()

        return {
            "state": state,
            "action": action,
            "feedback": feedback,
            "latency_seconds": latency_seconds,
            "reward": round(reward, 4),
        }
