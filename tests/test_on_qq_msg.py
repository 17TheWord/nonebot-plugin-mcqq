import time

import nonebot
from nonebot.adapters.minecraft import Adapter as MinecraftAdapter
from nonebot.adapters.minecraft import Bot as MinecraftBot
from nonebot.adapters.minecraft import MessageSegment as MCMessageSegment
from nonebot.adapters.minecraft.models import Color, Component
from nonebot.adapters.onebot.v11 import (
    Adapter as OneBotAdapter,
)
from nonebot.adapters.onebot.v11 import Bot as OneBot
from nonebot.adapters.onebot.v11 import (
    GroupMessageEvent as OneBotGroupMessageEvent,
)
from nonebot.adapters.onebot.v11 import Message
from nonebot.adapters.onebot.v11 import (
    Message as OneBotMessage,
)
from nonebot.adapters.onebot.v11.event import Sender as OneBotSender
from nonebot.adapters.qq import (
    Adapter as QQAdapter,
)
from nonebot.adapters.qq import Bot as QQBot
from nonebot.adapters.qq import (
    GuildMessageEvent as QQGuildMessageEvent,
)
from nonebot.adapters.qq.event import EventType
from nonebot.adapters.qq.models import User as QQUser
from nonebug import App
from nonebug.mixin.process import MatcherContext
import pytest


def make_onebot(ctx: MatcherContext):
    return ctx.create_bot(
        base=OneBot, adapter=nonebot.get_adapter(OneBotAdapter), self_id="123456789"
    )


def make_onebot_group_message_event(message: str, enable_superuser: bool = False):
    user_id = 999999999 if enable_superuser else 111111111
    return OneBotGroupMessageEvent(
        group_id=1234567890,
        self_id=123456789,
        post_type="message",
        sub_type="normal",
        message_type="group",
        font=0,
        user_id=user_id,
        message_id=1,
        message=OneBotMessage(message),
        original_message=OneBotMessage(message),
        raw_message=message,
        sender=OneBotSender(user_id=user_id, nickname="TestUser"),
        time=int(time.time()),
    )


def make_qq_guild_message_event(message: str):
    return QQGuildMessageEvent(
        id="1",
        channel_id="9876543210",
        guild_id="2001",
        author=QQUser(id="111111", username="TestUser"),
        __type__=EventType.MESSAGE_CREATE,
        content=message,
    )


@pytest.mark.asyncio
async def test_handle_onebot_msg(app: App):
    from nonebot_plugin_mcqq.on_qq_msg import on_qq_msg

    async with app.test_matcher(on_qq_msg) as ctx:
        mc_adapter = nonebot.get_adapter(MinecraftAdapter)

        one_bot = make_onebot(ctx)

        ctx.create_bot(
            base=MinecraftBot,
            adapter=mc_adapter,
            self_id="test_server",
        )

        onebot_message_event = make_onebot_group_message_event("test message")
        ctx.receive_event(one_bot, onebot_message_event)

        ctx.should_call_api(
            api="send_msg",
            data={
                "message": [
                    MCMessageSegment.text(text="TestUser", color=Color.green),
                    MCMessageSegment.text(
                        text="：",
                        color=Color.white,
                        extra=[Component(text="test message", color=Color.white)],
                    ),
                ]
            },
            # adapter=mc_adapter,
        )


@pytest.mark.asyncio
async def test_handle_qq_msg(app: App):
    from nonebot.adapters.qq.config import BotInfo

    from nonebot_plugin_mcqq.on_qq_msg import on_qq_msg

    async with app.test_matcher(on_qq_msg) as ctx:
        qq_adapter = nonebot.get_adapter(QQAdapter)
        mc_adapter = nonebot.get_adapter(MinecraftAdapter)

        bot_info = BotInfo(id="987654321", token="test_token", secret="test_secret")
        qq_bot = ctx.create_bot(
            base=QQBot, adapter=qq_adapter, self_id="987654321", bot_info=bot_info
        )

        ctx.create_bot(
            base=MinecraftBot,
            adapter=mc_adapter,
            self_id="test_server",
        )

        ctx.should_call_api(
            api="send_msg",
            data={
                "message": [
                    MCMessageSegment.text(text="TestUser", color=Color.green),
                    MCMessageSegment.text(
                        text="：",
                        color=Color.white,
                        extra=[Component(text="test message", color=Color.white)],
                    ),
                ]
            },
            # adapter=mc_adapter,
        )

        qq_guild_message_event = make_qq_guild_message_event("test message")
        ctx.receive_event(qq_bot, qq_guild_message_event)


@pytest.mark.asyncio
async def test_handle_qq_cmd_no_args(app: App):
    from nonebot_plugin_mcqq.on_qq_msg import on_qq_cmd

    async with app.test_matcher(on_qq_cmd) as ctx:
        mc_adapter = nonebot.get_adapter(MinecraftAdapter)
        ctx.create_bot(
            base=MinecraftBot,
            adapter=mc_adapter,
            self_id="test_server",
        )
        one_bot = make_onebot(ctx)

        event = make_onebot_group_message_event("/minecraft_command")
        ctx.receive_event(one_bot, event)
        ctx.should_call_send(event, "你没有输入命令", bot=one_bot)
        ctx.should_finished(on_qq_cmd)


@pytest.mark.asyncio
async def test_handle_qq_cmd(app: App):
    from nonebot_plugin_mcqq.on_qq_msg import on_qq_cmd

    mc_adapter = nonebot.get_adapter(MinecraftAdapter)

    async with app.test_matcher(on_qq_cmd) as ctx:
        ctx.create_bot(
            base=MinecraftBot,
            adapter=mc_adapter,
            self_id="test_server",
        )

        one_bot = make_onebot(ctx)

        event = make_onebot_group_message_event("/minecraft_command list")
        ctx.receive_event(one_bot, event)
        api = ctx.should_call_api(
            api="send_rcon_command",
            data={"command": "list"},
            result="test",
            # adapter=mc_adapter,
        )
        ctx.should_call_send(
            event=event,
            message=Message(f"[test_server] {api.result}"),
            bot=one_bot,
        )
        ctx.should_finished(on_qq_cmd)


@pytest.mark.asyncio
async def test_handle_title_cmd_no_permission(app: App):
    from nonebot_plugin_mcqq.on_qq_msg import on_qq_send_title_cmd

    mc_adapter = nonebot.get_adapter(MinecraftAdapter)

    async with app.test_matcher(on_qq_send_title_cmd) as ctx:
        ctx.create_bot(
            base=MinecraftBot,
            adapter=mc_adapter,
            self_id="test_server",
        )

        one_bot = make_onebot(ctx)

        event = make_onebot_group_message_event("/mcst Title")
        ctx.receive_event(one_bot, event)
        ctx.should_call_send(
            event=event,
            message="你没有权限使用此命令",
            bot=one_bot,
        )


@pytest.mark.asyncio
async def test_handle_title_cmd(app: App):
    from nonebot_plugin_mcqq.on_qq_msg import on_qq_send_title_cmd

    mc_adapter = nonebot.get_adapter(MinecraftAdapter)

    async with app.test_matcher(on_qq_send_title_cmd) as ctx:
        one_bot = make_onebot(ctx)
        ctx.create_bot(
            base=MinecraftBot,
            adapter=mc_adapter,
            self_id="test_server",
        )

        event = make_onebot_group_message_event("/mcst Title", True)
        ctx.receive_event(one_bot, event)
        api = ctx.should_call_api(
            api="send_title",
            data={"title": "Title", "subtitle": ""},
            result="发送 Title 成功",
            # adapter=mc_adapter,
        )
        ctx.should_call_send(
            event=event,
            message=Message(f"[test_server] {api.result}"),
            bot=one_bot,
        )


@pytest.mark.asyncio
async def test_handle_action_bar_cmd_no_permission(app: App):
    from nonebot_plugin_mcqq.on_qq_msg import on_qq_send_actionbar_cmd

    mc_adapter = nonebot.get_adapter(MinecraftAdapter)

    async with app.test_matcher(on_qq_send_actionbar_cmd) as ctx:
        ctx.create_bot(
            base=MinecraftBot,
            adapter=mc_adapter,
            self_id="test_server",
        )

        one_bot = make_onebot(ctx)

        event = make_onebot_group_message_event("/mcsa Action Bar")
        ctx.receive_event(one_bot, event)
        ctx.should_call_send(
            event=event,
            message="你没有权限使用此命令",
            bot=one_bot,
        )


@pytest.mark.asyncio
async def test_handle_action_bar_cmd(app: App):
    from nonebot_plugin_mcqq.on_qq_msg import on_qq_send_actionbar_cmd

    mc_adapter = nonebot.get_adapter(MinecraftAdapter)

    async with app.test_matcher(on_qq_send_actionbar_cmd) as ctx:
        ctx.create_bot(
            base=MinecraftBot,
            adapter=mc_adapter,
            self_id="test_server",
        )

        one_bot = make_onebot(ctx)

        event = make_onebot_group_message_event("/mcsa Action Bar", True)
        ctx.receive_event(one_bot, event)
        api = ctx.should_call_api(
            api="send_actionbar",
            data={"message": "Action Bar"},
            result=Message("发送 ActionBar 成功"),
            # adapter=mc_adapter,
        )
        ctx.should_call_send(
            event=event,
            message=Message(f"[test_server] {api.result}"),
            bot=one_bot,
        )
