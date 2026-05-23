import asyncio
from urllib.parse import quote_plus

import nonebot
from nonebot.adapters.minecraft import Adapter as MinecraftAdapter
from nonebot.adapters.onebot.v11 import Adapter as OneBotAdapter
from nonebot.adapters.onebot.v11 import Bot as OneBot
from nonebot.adapters.qq import Adapter as QQAdapter
from nonebot.adapters.qq import Bot as QQBot
from nonebot.adapters.qq.config import BotInfo
from nonebot.adapters.qq.models import Message as QQGuildMessage
from nonebot.adapters.qq.models import PostGroupMessagesReturn
from nonebot.adapters.qq.models import User as QQUser
from nonebug import App
import pytest


@pytest.fixture(autouse=True)
def reset_bot_manage_state(app):
    from nonebot_plugin_mcqq.config import plugin_config
    from nonebot_plugin_mcqq.data_source import (
        ONEBOT_GROUP_SERVER_DICT,
        QQ_GROUP_SERVER_DICT,
        QQ_GUILD_SERVER_DICT,
    )

    old_notice_connected = plugin_config.notice_connected
    old_onebot_mapping = dict(ONEBOT_GROUP_SERVER_DICT)
    old_qq_group_mapping = dict(QQ_GROUP_SERVER_DICT)
    old_qq_guild_mapping = dict(QQ_GUILD_SERVER_DICT)
    yield
    plugin_config.notice_connected = old_notice_connected
    ONEBOT_GROUP_SERVER_DICT.clear()
    ONEBOT_GROUP_SERVER_DICT.update(old_onebot_mapping)
    QQ_GROUP_SERVER_DICT.clear()
    QQ_GROUP_SERVER_DICT.update(old_qq_group_mapping)
    QQ_GUILD_SERVER_DICT.clear()
    QQ_GUILD_SERVER_DICT.update(old_qq_guild_mapping)


@pytest.mark.asyncio
async def test_on_bot_connected(app: App):
    """测试 Minecraft 服务器连接成功时的处理"""

    adapter = nonebot.get_adapter(MinecraftAdapter)

    async with app.test_server() as ctx:
        client = ctx.get_client()
        headers = {
            "x-self-name": quote_plus("Server"),
            "Authorization": "Bearer test_access_token",
        }
        client.headers.update(headers)
        async with client.websocket_connect("/minecraft/ws", headers=headers) as ws:
            await asyncio.sleep(1)
            assert "Server" in nonebot.get_bots()
            assert "Server" in adapter.bots
            await ws.close()

        await asyncio.sleep(1)
        assert "Server" not in nonebot.get_bots()
        assert "Server" not in adapter.bots


class FakeMinecraftBot:
    def __init__(self, self_id: str):
        self.self_id = self_id


@pytest.mark.asyncio
async def test_on_bot_connected_and_disconnected_updates_mappings(app: App):
    from nonebot_plugin_mcqq.bot_manage import on_bot_connected, on_bot_disconnected
    from nonebot_plugin_mcqq.data_source import (
        ONEBOT_GROUP_SERVER_DICT,
        QQ_GROUP_SERVER_DICT,
        QQ_GUILD_SERVER_DICT,
    )

    bot = FakeMinecraftBot("test_server")

    await on_bot_connected(bot)

    assert ONEBOT_GROUP_SERVER_DICT["1234567890"] == ["test_server"]
    assert QQ_GROUP_SERVER_DICT["654321"] == ["test_server"]
    assert QQ_GUILD_SERVER_DICT["9876543210"] == ["test_server"]

    await on_bot_disconnected(bot)

    assert "1234567890" not in ONEBOT_GROUP_SERVER_DICT
    assert "654321" not in QQ_GROUP_SERVER_DICT
    assert "9876543210" not in QQ_GUILD_SERVER_DICT


@pytest.mark.asyncio
async def test_on_bot_connected_ignores_unconfigured_server(app: App):
    from nonebot_plugin_mcqq.bot_manage import on_bot_connected
    from nonebot_plugin_mcqq.data_source import ONEBOT_GROUP_SERVER_DICT

    await on_bot_connected(FakeMinecraftBot("missing_server"))

    assert "missing_server" not in ONEBOT_GROUP_SERVER_DICT


@pytest.mark.asyncio
async def test_notify_groups_sends_connected_message(app: App):
    from nonebot_plugin_mcqq.bot_manage import notify_groups
    from nonebot_plugin_mcqq.config import plugin_config

    server = plugin_config.server_dict["test_server"]

    async with app.test_api() as ctx:
        ctx.create_bot(
            base=OneBot,
            adapter=nonebot.get_adapter(OneBotAdapter),
            self_id="123456789",
        )
        qq_group_bot_info = BotInfo(
            id="test_qq", token="test_token", secret="test_secret"
        )
        ctx.create_bot(
            base=QQBot,
            adapter=nonebot.get_adapter(QQAdapter),
            self_id="test_qq",
            bot_info=qq_group_bot_info,
        )
        qq_guild_bot_info = BotInfo(
            id="987654321", token="test_token", secret="test_secret"
        )
        ctx.create_bot(
            base=QQBot,
            adapter=nonebot.get_adapter(QQAdapter),
            self_id="987654321",
            bot_info=qq_guild_bot_info,
        )

        ctx.should_call_api(
            api="send_group_msg",
            data={
                "group_id": 1234567890,
                "message": "✅ 服务器 [test_server] 已成功连接！",
            },
            result={"message_id": 1},
        )
        ctx.should_call_api(
            api="post_group_messages",
            data={
                "group_openid": "654321",
                "msg_type": 0,
                "msg_id": None,
                "msg_seq": None,
                "event_id": None,
                "content": "✅ 服务器 [test_server] 已成功连接！",
                "media": None,
            },
            result=PostGroupMessagesReturn(id="1"),
        )
        ctx.should_call_api(
            api="post_messages",
            data={
                "channel_id": "9876543210",
                "msg_id": None,
                "event_id": None,
                "content": "✅ 服务器 [test_server] 已成功连接！",
            },
            result=QQGuildMessage(
                id="2",
                channel_id="9876543210",
                guild_id="2001",
                content="✅ 服务器 [test_server] 已成功连接！",
                author=QQUser(id="987654321"),
            ),
        )

        await notify_groups(server, "test_server", connected=True)


@pytest.mark.asyncio
async def test_notify_groups_skips_missing_bots(app: App):
    from nonebot_plugin_mcqq.bot_manage import notify_groups
    from nonebot_plugin_mcqq.config import plugin_config

    async with app.test_api():
        await notify_groups(
            plugin_config.server_dict["test_server"], "test_server", False
        )
