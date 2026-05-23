import time
import uuid

import nonebot
from nonebot.adapters.minecraft import (
    AchievementModel,
    DisplayModel,
    Player,
    PlayerAchievementEvent,
    PlayerChatEvent,
    PlayerCommandEvent,
    PlayerDeathEvent,
    PlayerJoinEvent,
    PlayerQuitEvent,
    Translate,
)
from nonebot.adapters.minecraft import (
    Adapter as MinecraftAdapter,
)
from nonebot.adapters.minecraft import (
    Bot as MinecraftBot,
)
from nonebot.adapters.minecraft import (
    Message as MinecraftMessage,
)
from nonebot.adapters.qq import Adapter as QQAdapter
from nonebot.adapters.qq import Bot as QQBot
from nonebot.adapters.qq.models import PostGroupMessagesReturn
from nonebug import App
import pytest

base_player = Player(uuid=uuid.uuid4(), nickname="test_player")

base_event = {
    "server_name": "test_server",
    "server_version": "test_version",
    "server_type": "test_type",
    "timestamp": int(time.time()),
    "player": base_player,
}


@pytest.mark.asyncio
async def test_handle_mc_msg(app: App):
    """测试 Minecraft 聊天消息的处理"""
    from nonebot.adapters.qq.config import BotInfo

    from nonebot_plugin_mcqq.on_minecraft_msg import on_mc_msg

    mc_adapter = nonebot.get_adapter(MinecraftAdapter)
    qq_adapter = nonebot.get_adapter(QQAdapter)

    async with app.test_matcher(on_mc_msg) as ctx:
        bot_info = BotInfo(id="test_qq", token="test_token", secret="test_secret")
        ctx.create_bot(
            base=QQBot, adapter=qq_adapter, self_id="test_qq", bot_info=bot_info
        )
        # 创建 Minecraft Bot
        mc_bot = ctx.create_bot(
            base=MinecraftBot, adapter=mc_adapter, self_id="test_server"
        )

        player_chat_event = PlayerChatEvent(
            **base_event,
            event_name="PlayerChatEvent",
            post_type="message",
            sub_type="player_chat",
            message=MinecraftMessage("Hello from Minecraft!"),
        )

        # 接收聊天事件
        ctx.receive_event(mc_bot, player_chat_event)

        # 同步聊天信息至 QQ适配器群
        ctx.should_call_api(
            api="post_group_messages",
            data={
                "group_openid": "654321",
                "msg_type": 0,
                "content": "test_player：Hello from Minecraft!",
            },
            result=PostGroupMessagesReturn(id="1"),
        )

        # Mock 需要被过滤的消息
        player_chat_event = PlayerChatEvent(
            **base_event,
            event_name="PlayerChatEvent",
            post_type="message",
            sub_type="player_chat",
            message=MinecraftMessage("!!This message should be ignored"),
        )

        # 接收被过滤的消息，但不发送
        ctx.receive_event(mc_bot, player_chat_event)

        # Mock 命令事件
        player_command_event = PlayerCommandEvent(
            **base_event,
            event_name="PlayerCommandEvent",
            post_type="message",
            sub_type="player_command",
            command="/say Hello Command!",
        )

        # 接收命令事件
        ctx.receive_event(mc_bot, player_command_event)


@pytest.mark.asyncio
async def test_handle_mc_notice(app: App):
    """测试 Minecraft 加入和离开消息的处理"""
    from nonebot_plugin_mcqq.on_minecraft_msg import on_mc_notice

    mc_adapter = nonebot.get_adapter(MinecraftAdapter)

    async with app.test_matcher(on_mc_notice) as ctx:
        mc_bot = ctx.create_bot(
            base=MinecraftBot, adapter=mc_adapter, self_id="test_server"
        )

        player_join_event = PlayerJoinEvent(
            **base_event,
            event_name="PlayerJoinEvent",
            post_type="notice",
            sub_type="player_join",
        )

        ctx.receive_event(mc_bot, player_join_event)

        player_quit_event = PlayerQuitEvent(
            **base_event,
            event_name="PlayerQuitEvent",
            post_type="notice",
            sub_type="player_quit",
        )

        ctx.receive_event(mc_bot, player_quit_event)

        death = Translate(
            key="minecraft:generic",
            args=[Translate(text="test_player"), Translate(text="Zombie")],
            text="test_player was slain by Zombie",
        )

        player_death_event = PlayerDeathEvent(
            **base_event,
            event_name="PlayerDeathEvent",
            post_type="notice",
            sub_type="player_death",
            death=death,
        )

        ctx.receive_event(mc_bot, player_death_event)

        display = DisplayModel(
            title=Translate(text="minecraft:achievement.get_wood"),
            frame="goal",
            description=Translate(text="minecraft:achievement.get_wood.desc"),
        )

        achievement = AchievementModel(
            key="minecraft:achievement.get_wood",
            display=display,
            translate=Translate(
                text="Player has earned the achievement [Getting Wood]"
            ),
        )

        player_achievement_event = PlayerAchievementEvent(
            **base_event,
            event_name="PlayerAchievementEvent",
            post_type="notice",
            sub_type="player_achievement",
            achievement=achievement,
        )
        ctx.receive_event(mc_bot, player_achievement_event)
