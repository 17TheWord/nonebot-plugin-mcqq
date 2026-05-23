import nonebot
from nonebot.adapters.minecraft.models import ClickAction, Color
from nonebot.adapters.onebot.v11 import Message as OneBotMessage
from nonebot.adapters.onebot.v11 import MessageSegment as OneBotMessageSegment
from nonebot.adapters.qq import Adapter as QQAdapter
from nonebot.adapters.qq import Bot as QQBot
from nonebot.adapters.qq import Message as QQMessage
from nonebot.adapters.qq import MessageSegment as QQMessageSegment
from nonebot.adapters.qq.config import BotInfo
from nonebug import App
import pytest

from tests.test_on_qq_msg import (
    make_onebot_group_message_event,
    make_qq_guild_message_event,
)


@pytest.fixture(autouse=True)
def reset_parse_config(app):
    from nonebot_plugin_mcqq.config import plugin_config

    old_send_group_name = plugin_config.send_group_name
    old_chat_image_enable = plugin_config.chat_image_enable
    yield
    plugin_config.send_group_name = old_send_group_name
    plugin_config.chat_image_enable = old_chat_image_enable


@pytest.fixture
def patch_names(monkeypatch):
    import nonebot_plugin_mcqq.utils.parse_qq_msg as parse_qq_msg

    async def fake_get_group_or_nick_name(bot, event, user_id=None):
        if user_id is None:
            return "TestGroup"
        if user_id == "222222222":
            return "OtherUser"
        return "Sender"

    async def fake_get_qq_channel_name(bot, channel_id):
        return "General"

    monkeypatch.setattr(
        parse_qq_msg, "get_group_or_nick_name", fake_get_group_or_nick_name
    )
    monkeypatch.setattr(parse_qq_msg, "get_qq_channel_name", fake_get_qq_channel_name)


def get_extra_components(message):
    return message[-1].data["extra"]


@pytest.mark.asyncio
async def test_parse_onebot_text_normalizes_newlines(app, patch_names):
    from nonebot_plugin_mcqq.utils.parse_qq_msg import parse_qq_msg_to_component

    event = make_onebot_group_message_event("hello\r\nworld")

    message, log_text = await parse_qq_msg_to_component(bot=object(), event=event)

    extras = get_extra_components(message)

    assert extras[0]["text"] == "hello\n * world"
    assert extras[0]["color"] == Color.white
    assert log_text == "Sender ：hello\n * world "


@pytest.mark.asyncio
async def test_parse_onebot_image_creates_clickable_component(app, patch_names):
    from nonebot_plugin_mcqq.utils.parse_qq_msg import parse_qq_msg_to_component

    event = make_onebot_group_message_event("placeholder")
    event.message = OneBotMessage(
        OneBotMessageSegment("image", {"url": "example.com/image.png"})
    )

    message, log_text = await parse_qq_msg_to_component(bot=object(), event=event)
    image_component = get_extra_components(message)[0]

    assert image_component["text"] == "[图片]"
    assert image_component["color"] == Color.light_purple
    assert image_component["clickEvent"]["action"] == ClickAction.open_url
    assert image_component["clickEvent"]["value"] == "https://example.com/image.png"
    assert image_component["hoverEvent"]["contents"][0]["text"] == "点击查看图片"
    assert log_text == "Sender ：[图片] "


@pytest.mark.asyncio
async def test_parse_onebot_image_uses_chat_image_code_when_enabled(app, patch_names):
    from nonebot_plugin_mcqq.config import plugin_config
    from nonebot_plugin_mcqq.utils.parse_qq_msg import parse_qq_msg_to_component

    plugin_config.chat_image_enable = True
    event = make_onebot_group_message_event("placeholder")
    event.message = OneBotMessage(
        OneBotMessageSegment("image", {"url": "example.com/image.png"})
    )

    message, log_text = await parse_qq_msg_to_component(bot=object(), event=event)
    image_component = get_extra_components(message)[0]

    assert image_component["text"] == "[[CICode,url=https://example.com/image.png]]"
    assert log_text == "Sender ：[图片] "


@pytest.mark.asyncio
async def test_parse_onebot_at_and_unknown_segments(app, patch_names):
    from nonebot_plugin_mcqq.utils.parse_qq_msg import parse_qq_msg_to_component

    event = make_onebot_group_message_event("placeholder")
    event.message = OneBotMessage(
        [
            OneBotMessageSegment.at("all"),
            OneBotMessageSegment.at("222222222"),
            OneBotMessageSegment("custom", {}),
        ]
    )

    message, log_text = await parse_qq_msg_to_component(bot=object(), event=event)
    extras = get_extra_components(message)

    assert [component["text"] for component in extras] == [
        "@全体成员",
        "@OtherUser",
        "[未知消息类型 custom]",
    ]
    assert log_text == "Sender ：@全体成员 @OtherUser [未知消息类型 custom] "


@pytest.mark.asyncio
async def test_parse_onebot_media_share_face_and_record_segments(app, patch_names):
    from nonebot_plugin_mcqq.utils.parse_qq_msg import parse_qq_msg_to_component

    event = make_onebot_group_message_event("placeholder")
    event.message = OneBotMessage(
        [
            OneBotMessageSegment("video", {"url": "example.com/video.mp4"}),
            OneBotMessageSegment("share", {"url": "example.com/share"}),
            OneBotMessageSegment("face", {}),
            OneBotMessageSegment("record", {}),
        ]
    )

    message, log_text = await parse_qq_msg_to_component(bot=object(), event=event)
    extras = get_extra_components(message)

    assert [component["text"] for component in extras] == [
        "[视频]",
        "[分享]",
        "[表情]",
        "[语音]",
    ]
    assert extras[0]["clickEvent"]["value"] == "https://example.com/video.mp4"
    assert extras[1]["clickEvent"]["value"] == "https://example.com/share"
    assert log_text == "Sender ：[视频] [分享] [表情] [语音] "


@pytest.mark.asyncio
async def test_parse_qq_mention_user_and_everyone(app, patch_names):
    from nonebot_plugin_mcqq.utils.parse_qq_msg import parse_qq_msg_to_component

    event = make_qq_guild_message_event("placeholder")
    event.message = QQMessage(
        [
            QQMessageSegment.mention_user("222222222"),
            QQMessageSegment.mention_everyone(),
            QQMessageSegment.emoji("123"),
        ]
    )

    message, log_text = await parse_qq_msg_to_component(bot=object(), event=event)
    extras = get_extra_components(message)

    assert [component["text"] for component in extras] == [
        "OtherUser",
        "@全体成员",
        "[表情]",
    ]
    assert log_text == "Sender ：OtherUser @全体成员 [表情] "


@pytest.mark.asyncio
async def test_parse_includes_group_name_when_enabled(app, patch_names):
    from nonebot_plugin_mcqq.config import plugin_config
    from nonebot_plugin_mcqq.utils.parse_qq_msg import parse_qq_msg_to_component

    plugin_config.send_group_name = True
    event = make_onebot_group_message_event("hello")

    message, log_text = await parse_qq_msg_to_component(bot=object(), event=event)

    assert message[0].data["text"] == "TestGroup "
    assert message[0].data["color"] == Color.aqua
    assert log_text == "TestGroup Sender ：hello "


@pytest.mark.asyncio
async def test_parse_qq_guild_mention_channel(app: App, patch_names):
    from nonebot_plugin_mcqq.utils.parse_qq_msg import parse_qq_msg_to_component

    async with app.test_api() as ctx:
        bot_info = BotInfo(id="987654321", token="test_token", secret="test_secret")
        qq_bot = ctx.create_bot(
            base=QQBot,
            adapter=nonebot.get_adapter(QQAdapter),
            self_id="987654321",
            bot_info=bot_info,
        )
        event = make_qq_guild_message_event("placeholder")
        event.message = QQMessage(QQMessageSegment.mention_channel("9876543210"))

        message, log_text = await parse_qq_msg_to_component(bot=qq_bot, event=event)

    mention_component = get_extra_components(message)[0]
    assert mention_component["text"] == "@General"
    assert mention_component["color"] == Color.green
    assert log_text == "Sender ：@General "
