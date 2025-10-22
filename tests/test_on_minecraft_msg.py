import time
import uuid

from nonebot import get_adapter
from nonebot.adapters.minecraft import (
    Adapter as MinecraftAdapter,
)
from nonebot.adapters.minecraft import (
    BaseChatEvent,
    BaseDeathEvent,
    BaseJoinEvent,
    BasePlayer,
    BasePlayerCommandEvent,
    BaseQuitEvent,
)
from nonebot.adapters.minecraft import (
    Bot as MinecraftBot,
)
from nonebot.adapters.minecraft import (
    Message as MinecraftMessage,
)
from nonebug import App
import pytest

base_player = BasePlayer(uuid=uuid.uuid4(), nickname="test_player")

base_event = {
    "server_name": "test_server",
    "event_name": "test_event",
    "server_version": "test_version",
    "server_type": "test_type",
    "timestamp": int(time.time()),
    "player": base_player,
}


@pytest.mark.asyncio
async def test_handle_mc_chat_event(app: App):
    """测试 Minecraft 聊天消息的处理"""
    from nonebot_plugin_mcqq.on_minecraft_msg import on_mc_msg

    mc_adapter = get_adapter(MinecraftAdapter)

    async with app.test_matcher(on_mc_msg) as ctx:
        # 创建 Minecraft Bot
        mc_bot = ctx.create_bot(
            base=MinecraftBot, adapter=mc_adapter, self_id="test_server"
        )

        base_chat_event = BaseChatEvent(
            **base_event,
            post_type="message",
            sub_type="chat",
            message=MinecraftMessage("Hello from Minecraft!"),
        )

        ctx.receive_event(mc_bot, base_chat_event)


@pytest.mark.asyncio
async def test_handle_mc_command_event(app: App):
    """测试 Minecraft 指令消息的处理"""
    from nonebot_plugin_mcqq.on_minecraft_msg import on_mc_msg

    mc_adapter = get_adapter(MinecraftAdapter)

    async with app.test_matcher(on_mc_msg) as ctx:
        # 创建 Minecraft Bot
        mc_bot = ctx.create_bot(
            base=MinecraftBot, adapter=mc_adapter, self_id="test_server"
        )

        base_command_event = BasePlayerCommandEvent(
            **base_event,
            post_type="message",
            sub_type="player_command",
            message=MinecraftMessage("/test command"),
        )

        ctx.receive_event(mc_bot, base_command_event)


@pytest.mark.asyncio
async def test_handle_mc_death_event(app: App):
    """测试 Minecraft 死亡消息的处理"""
    from nonebot_plugin_mcqq.on_minecraft_msg import on_mc_msg

    mc_adapter = get_adapter(MinecraftAdapter)

    async with app.test_matcher(on_mc_msg) as ctx:
        mc_bot = ctx.create_bot(
            base=MinecraftBot, adapter=mc_adapter, self_id="test_server"
        )

        base_death_event = BaseDeathEvent(
            **base_event,
            post_type="message",
            sub_type="death",
            message=MinecraftMessage("You died!"),
        )

        ctx.receive_event(mc_bot, base_death_event)


@pytest.mark.asyncio
async def test_handle_mc_join_quit_event(app: App):
    """测试 Minecraft 加入和离开消息的处理"""
    from nonebot_plugin_mcqq.on_minecraft_msg import on_mc_msg

    mc_adapter = get_adapter(MinecraftAdapter)

    async with app.test_matcher(on_mc_msg) as ctx:
        mc_bot = ctx.create_bot(
            base=MinecraftBot, adapter=mc_adapter, self_id="test_server"
        )

        base_join_event = BaseJoinEvent(
            **base_event,
            post_type="notice",
            sub_type="join",
        )

        ctx.receive_event(mc_bot, base_join_event)

        base_quit_event = BaseQuitEvent(
            **base_event,
            post_type="notice",
            sub_type="quit",
        )

        ctx.receive_event(mc_bot, base_quit_event)
