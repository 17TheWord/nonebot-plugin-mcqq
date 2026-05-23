import importlib.util
from pathlib import Path

import pytest


def test_mcqq_config_converts_common_set_values(app):
    from nonebot_plugin_mcqq.config import MCQQConfig

    config = MCQQConfig(
        command_header="mcc",
        ignore_message_header=["#", "!"],
        ignore_word_list={"bad", "word"},
    )

    assert config.command_header == {"mcc"}
    assert config.ignore_message_header == {"#", "!"}
    assert config.ignore_word_list == {"bad", "word"}


def test_mcqq_config_uses_fallback_for_invalid_common_set_values(app):
    from nonebot_plugin_mcqq.config import MCQQConfig

    config = MCQQConfig(command_header=123, ignore_message_header=123)

    assert config.command_header == {"mcqq"}
    assert config.ignore_message_header == set()


@pytest.mark.parametrize("priority", [0, 99])
def test_mcqq_config_invalid_command_priority_falls_back_to_default(app, priority):
    from nonebot_plugin_mcqq.config import MCQQConfig

    config = MCQQConfig(command_priority=priority)

    assert config.command_priority == 98


def test_mcqq_config_accepts_valid_command_priority(app):
    from nonebot_plugin_mcqq.config import MCQQConfig

    config = MCQQConfig(command_priority=1)

    assert config.command_priority == 1


def test_mcqq_config_disables_rcon_result_image_without_pillow(app, monkeypatch):
    from nonebot_plugin_mcqq.config import MCQQConfig

    real_find_spec = importlib.util.find_spec

    def fake_find_spec(name: str):
        if name == "PIL":
            return None
        return real_find_spec(name)

    monkeypatch.setattr(importlib.util, "find_spec", fake_find_spec)

    config = MCQQConfig(rcon_result_to_image=True)

    assert config.rcon_result_to_image is False


def test_mcqq_config_ttf_path_uses_existing_path(app, tmp_path: Path):
    from nonebot_plugin_mcqq.config import MCQQConfig

    font_path = tmp_path.joinpath("font.ttf")
    font_path.write_bytes(b"font")

    config = MCQQConfig(ttf_path=font_path)

    assert config.ttf_path == font_path
