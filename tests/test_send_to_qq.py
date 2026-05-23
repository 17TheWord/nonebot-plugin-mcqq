import nonebot
from nonebot.adapters.onebot.v11 import Adapter as OneBotAdapter
from nonebot.adapters.onebot.v11 import Bot as OneBot
from nonebot.adapters.qq import Adapter as QQAdapter
from nonebot.adapters.qq import AuditException
from nonebot.adapters.qq import Bot as QQBot
from nonebot.adapters.qq.config import BotInfo
from nonebot.adapters.qq.models import Message as QQGuildMessage
from nonebot.adapters.qq.models import PostGroupMessagesReturn
from nonebot.adapters.qq.models import User as QQUser
from nonebug import App
import pytest


@pytest.fixture(autouse=True)
def reset_send_to_qq_config(app):
    from nonebot_plugin_mcqq.config import plugin_config

    old_display_server_name = plugin_config.display_server_name
    yield
    plugin_config.display_server_name = old_display_server_name


@pytest.mark.asyncio
async def test_send_mc_msg_to_groups_and_guild(app: App):
    from nonebot_plugin_mcqq.utils.send_to_qq import send_mc_msg_to_qq

    async with app.test_api() as ctx:
        ctx.create_bot(
            base=OneBot,
            adapter=nonebot.get_adapter(OneBotAdapter),
            self_id="123456789",
        )
        bot_info = BotInfo(id="test_qq", token="test_token", secret="test_secret")
        ctx.create_bot(
            base=QQBot,
            adapter=nonebot.get_adapter(QQAdapter),
            self_id="test_qq",
            bot_info=bot_info,
        )
        guild_bot_info = BotInfo(
            id="987654321", token="test_token", secret="test_secret"
        )
        ctx.create_bot(
            base=QQBot,
            adapter=nonebot.get_adapter(QQAdapter),
            self_id="987654321",
            bot_info=guild_bot_info,
        )

        ctx.should_call_api(
            api="send_group_msg",
            data={"group_id": 1234567890, "message": "GreenRed"},
            result={"message_id": 1},
        )
        ctx.should_call_api(
            api="post_group_messages",
            data={
                "group_openid": "654321",
                "msg_type": 0,
                "content": "GreenRed",
            },
            result=PostGroupMessagesReturn(id="1"),
        )
        ctx.should_call_api(
            api="post_messages",
            data={
                "channel_id": "9876543210",
                "msg_id": None,
                "event_id": None,
                "content": "GreenRed",
            },
            result=QQGuildMessage(
                id="2",
                channel_id="9876543210",
                guild_id="2001",
                content="GreenRed",
                author=QQUser(id="987654321"),
            ),
        )

        await send_mc_msg_to_qq("test_server", "&aGreen§cRed")


@pytest.mark.asyncio
async def test_send_mc_msg_to_qq_handles_missing_server(app: App):
    from nonebot_plugin_mcqq.utils.send_to_qq import send_mc_msg_to_qq

    async with app.test_api():
        await send_mc_msg_to_qq("missing_server", "message")


@pytest.mark.asyncio
async def test_send_mc_msg_to_qq_handles_missing_bot(app: App):
    from nonebot_plugin_mcqq.utils.send_to_qq import send_mc_msg_to_qq

    async with app.test_api():
        await send_mc_msg_to_qq("test_server", "message")


@pytest.mark.asyncio
async def test_send_mc_msg_to_qq_handles_guild_audit(monkeypatch, app: App):
    from nonebot_plugin_mcqq.utils.send_to_qq import send_mc_msg_to_qq

    class FakeAuditResult:
        def get_event_name(self):
            return "MESSAGE_AUDIT_PASS"

    class FakeAuditException(AuditException):
        async def get_audit_result(self, timeout):
            assert timeout == 3
            return FakeAuditResult()

    async with app.test_api() as ctx:
        ctx.create_bot(
            base=OneBot,
            adapter=nonebot.get_adapter(OneBotAdapter),
            self_id="123456789",
        )
        bot_info = BotInfo(id="test_qq", token="test_token", secret="test_secret")
        ctx.create_bot(
            base=QQBot,
            adapter=nonebot.get_adapter(QQAdapter),
            self_id="test_qq",
            bot_info=bot_info,
        )
        guild_bot_info = BotInfo(
            id="987654321", token="test_token", secret="test_secret"
        )
        ctx.create_bot(
            base=QQBot,
            adapter=nonebot.get_adapter(QQAdapter),
            self_id="987654321",
            bot_info=guild_bot_info,
        )

        ctx.should_call_api(
            api="send_group_msg",
            data={"group_id": 1234567890, "message": "message"},
            result={"message_id": 1},
        )
        ctx.should_call_api(
            api="post_group_messages",
            data={
                "group_openid": "654321",
                "msg_type": 0,
                "content": "message",
            },
            result=PostGroupMessagesReturn(id="1"),
        )
        ctx.should_call_api(
            api="post_messages",
            data={
                "channel_id": "9876543210",
                "msg_id": None,
                "event_id": None,
                "content": "message",
            },
            exception=FakeAuditException("audit_id"),
        )

        await send_mc_msg_to_qq("test_server", "message")


@pytest.mark.asyncio
async def test_send_mc_msg_to_qq_continues_when_group_audit_result_fails(app: App):
    from nonebot_plugin_mcqq.utils.send_to_qq import send_mc_msg_to_qq

    class FakeAuditException(AuditException):
        async def get_audit_result(self, timeout):
            assert timeout == 3
            raise RuntimeError("audit timeout")

    async with app.test_api() as ctx:
        ctx.create_bot(
            base=OneBot,
            adapter=nonebot.get_adapter(OneBotAdapter),
            self_id="123456789",
        )
        bot_info = BotInfo(id="test_qq", token="test_token", secret="test_secret")
        ctx.create_bot(
            base=QQBot,
            adapter=nonebot.get_adapter(QQAdapter),
            self_id="test_qq",
            bot_info=bot_info,
        )
        guild_bot_info = BotInfo(
            id="987654321", token="test_token", secret="test_secret"
        )
        ctx.create_bot(
            base=QQBot,
            adapter=nonebot.get_adapter(QQAdapter),
            self_id="987654321",
            bot_info=guild_bot_info,
        )

        ctx.should_call_api(
            api="send_group_msg",
            data={"group_id": 1234567890, "message": "message"},
            result={"message_id": 1},
        )
        ctx.should_call_api(
            api="post_group_messages",
            data={
                "group_openid": "654321",
                "msg_type": 0,
                "content": "message",
            },
            exception=FakeAuditException("audit_id"),
        )
        ctx.should_call_api(
            api="post_messages",
            data={
                "channel_id": "9876543210",
                "msg_id": None,
                "event_id": None,
                "content": "message",
            },
            result=QQGuildMessage(
                id="2",
                channel_id="9876543210",
                guild_id="2001",
                content="message",
                author=QQUser(id="987654321"),
            ),
        )

        await send_mc_msg_to_qq("test_server", "message")


@pytest.mark.asyncio
async def test_send_mc_msg_to_qq_handles_channel_audit_result_failure(app: App):
    from nonebot_plugin_mcqq.utils.send_to_qq import send_mc_msg_to_qq

    class FakeAuditException(AuditException):
        async def get_audit_result(self, timeout):
            assert timeout == 3
            raise RuntimeError("audit timeout")

    async with app.test_api() as ctx:
        ctx.create_bot(
            base=OneBot,
            adapter=nonebot.get_adapter(OneBotAdapter),
            self_id="123456789",
        )
        bot_info = BotInfo(id="test_qq", token="test_token", secret="test_secret")
        ctx.create_bot(
            base=QQBot,
            adapter=nonebot.get_adapter(QQAdapter),
            self_id="test_qq",
            bot_info=bot_info,
        )
        guild_bot_info = BotInfo(
            id="987654321", token="test_token", secret="test_secret"
        )
        ctx.create_bot(
            base=QQBot,
            adapter=nonebot.get_adapter(QQAdapter),
            self_id="987654321",
            bot_info=guild_bot_info,
        )

        ctx.should_call_api(
            api="send_group_msg",
            data={"group_id": 1234567890, "message": "message"},
            result={"message_id": 1},
        )
        ctx.should_call_api(
            api="post_group_messages",
            data={
                "group_openid": "654321",
                "msg_type": 0,
                "content": "message",
            },
            result=PostGroupMessagesReturn(id="1"),
        )
        ctx.should_call_api(
            api="post_messages",
            data={
                "channel_id": "9876543210",
                "msg_id": None,
                "event_id": None,
                "content": "message",
            },
            exception=FakeAuditException("audit_id"),
        )

        await send_mc_msg_to_qq("test_server", "message")


@pytest.mark.asyncio
async def test_send_mc_msg_to_qq_includes_server_name_when_enabled(app: App):
    from nonebot_plugin_mcqq.config import plugin_config
    from nonebot_plugin_mcqq.utils.send_to_qq import send_mc_msg_to_qq

    plugin_config.display_server_name = True

    async with app.test_api() as ctx:
        ctx.create_bot(
            base=OneBot,
            adapter=nonebot.get_adapter(OneBotAdapter),
            self_id="123456789",
        )
        bot_info = BotInfo(id="test_qq", token="test_token", secret="test_secret")
        ctx.create_bot(
            base=QQBot,
            adapter=nonebot.get_adapter(QQAdapter),
            self_id="test_qq",
            bot_info=bot_info,
        )
        guild_bot_info = BotInfo(
            id="987654321", token="test_token", secret="test_secret"
        )
        ctx.create_bot(
            base=QQBot,
            adapter=nonebot.get_adapter(QQAdapter),
            self_id="987654321",
            bot_info=guild_bot_info,
        )

        ctx.should_call_api(
            api="send_group_msg",
            data={"group_id": 1234567890, "message": "[test_server] message"},
            result={"message_id": 1},
        )
        ctx.should_call_api(
            api="post_group_messages",
            data={
                "group_openid": "654321",
                "msg_type": 0,
                "content": "[test_server] message",
            },
            result=PostGroupMessagesReturn(id="1"),
        )
        ctx.should_call_api(
            api="post_messages",
            data={
                "channel_id": "9876543210",
                "msg_id": None,
                "event_id": None,
                "content": "[test_server] message",
            },
            result=QQGuildMessage(
                id="2",
                channel_id="9876543210",
                guild_id="2001",
                content="[test_server] message",
                author=QQUser(id="987654321"),
            ),
        )

        await send_mc_msg_to_qq("test_server", "message")
