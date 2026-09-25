from app.agent.prompts import CONFIG_A, CONFIG_B


def test_configs_are_different():
    assert CONFIG_A["name"] != CONFIG_B["name"]
    assert CONFIG_A["top_k"] != CONFIG_B["top_k"]
    assert CONFIG_A["system_prompt"] != CONFIG_B["system_prompt"]


def test_config_a():
    assert CONFIG_A["top_k"] == 3
    assert CONFIG_A["name"] == "focused_support"


def test_config_b():
    assert CONFIG_B["top_k"] == 5
    assert CONFIG_B["name"] == "verified_support"
