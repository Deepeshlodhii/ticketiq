import random

from app.rl.bandit import ContextualBandit


def run_experiment():
    random.seed(42)

    bandit = ContextualBandit(epsilon=0.10)

    state = "billing|medium|premium"

    before_counts = {
        "config_a": 0,
        "config_b": 0,
    }

    after_counts = {
        "config_a": 0,
        "config_b": 0,
    }

    # Phase 1:
    # Config A performs better.
    for _ in range(100):
        result = bandit.select_action(
            category="billing",
            urgency_score=0.35,
            tier="premium",
        )

        action = result["action"]
        before_counts[action] += 1

        if action == "config_a":
            feedback = 1
        else:
            feedback = 0

        bandit.update(
            state=state,
            action=action,
            feedback=feedback,
            latency_seconds=1.0,
        )

    # Phase 2:
    # Environment changes:
    # Config B now performs better.
    for _ in range(100):
        result = bandit.select_action(
            category="billing",
            urgency_score=0.35,
            tier="premium",
        )

        action = result["action"]
        after_counts[action] += 1

        if action == "config_b":
            feedback = 1
        else:
            feedback = 0

        bandit.update(
            state=state,
            action=action,
            feedback=feedback,
            latency_seconds=1.0,
        )

    print("\n=== RL Distribution Shift Experiment ===")

    print("\nBefore distribution shift:")
    print(before_counts)

    print("\nAfter distribution shift:")
    print(after_counts)

    print("\nInterpretation:")
    print(
        "The environment changes so that config_b becomes "
        "the better configuration. The contextual bandit "
        "receives feedback and adapts its action selection."
    )


if __name__ == "__main__":
    run_experiment()
