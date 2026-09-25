from app.rl.bandit import ContextualBandit


def test_state_creation():
    bandit = ContextualBandit()

    state = bandit.build_state(
        category="billing",
        urgency_score=0.8,
        tier="premium",
    )

    assert state == "billing|critical|premium"


def test_action_selection():
    bandit = ContextualBandit(epsilon=0.0)

    result = bandit.select_action(
        category="billing",
        urgency_score=0.8,
        tier="premium",
    )

    assert result["action"] in {
        "config_a",
        "config_b",
    }


def test_reward_update():
    bandit = ContextualBandit()

    result = bandit.update(
        state="billing|high|premium",
        action="config_a",
        feedback=1,
        latency_seconds=2.0,
    )

    assert result["reward"] == 8.0


def test_negative_reward():
    bandit = ContextualBandit()

    result = bandit.update(
        state="technical|critical|premium",
        action="config_b",
        feedback=0,
        latency_seconds=2.0,
    )

    assert result["reward"] == -2.0
