import pytest


@pytest.fixture
def reset_rcon_result_to_image(app):
    from nonebot_plugin_mcqq.config import plugin_config

    old_value = plugin_config.rcon_result_to_image
    yield
    plugin_config.rcon_result_to_image = old_value


def test_get_title_splits_on_first_newline(app):
    from nonebot_plugin_mcqq.utils import get_title

    assert get_title("Title") == ("Title", "")
    assert get_title("Title\nSubtitle") == ("Title", "Subtitle")
    assert get_title("Title\nSubtitle\nMore") == ("Title", "Subtitle\nMore")


def test_get_rcon_result_returns_clean_text_for_onebot_event(app):
    from nonebot.adapters.onebot.v11 import MessageSegment

    from nonebot_plugin_mcqq.utils import get_rcon_result
    from tests.test_on_qq_msg import make_onebot_group_message_event

    event = make_onebot_group_message_event("/minecraft_command list")
    result = get_rcon_result("&aGreen §cRed", event)

    assert result == MessageSegment.text("Green Red")


def test_get_rcon_result_returns_clean_text_for_qq_event(app):
    from nonebot.adapters.qq import MessageSegment

    from nonebot_plugin_mcqq.utils import get_rcon_result
    from tests.test_on_qq_msg import make_qq_group_message_event

    event = make_qq_group_message_event("/minecraft_command list")
    result = get_rcon_result("&aGreen §cRed", event)

    assert result == MessageSegment.text("Green Red")


def test_get_rcon_result_returns_image_for_onebot_event(
    app, monkeypatch, reset_rcon_result_to_image
):
    from nonebot.adapters.onebot.v11 import MessageSegment

    from nonebot_plugin_mcqq.config import plugin_config
    import nonebot_plugin_mcqq.utils as utils
    from tests.test_on_qq_msg import make_onebot_group_message_event

    monkeypatch.setattr(
        utils, "draw_result_image", lambda result: b"png-bytes", raising=False
    )
    plugin_config.rcon_result_to_image = True

    event = make_onebot_group_message_event("/minecraft_command list")
    result = utils.get_rcon_result("&aGreen", event)

    assert result == MessageSegment.image(b"png-bytes")


def test_get_rcon_result_returns_image_for_qq_event(
    app, monkeypatch, reset_rcon_result_to_image
):
    from nonebot.adapters.qq import MessageSegment

    from nonebot_plugin_mcqq.config import plugin_config
    import nonebot_plugin_mcqq.utils as utils
    from tests.test_on_qq_msg import make_qq_group_message_event

    monkeypatch.setattr(
        utils, "draw_result_image", lambda result: b"png-bytes", raising=False
    )
    plugin_config.rcon_result_to_image = True

    event = make_qq_group_message_event("/minecraft_command list")
    result = utils.get_rcon_result("&aGreen", event)

    assert result == MessageSegment.file_image(b"png-bytes")
