import time
import uuid

import nonebot
from nonebot.adapters.minecraft import (
    AchievementModel,
    DeathModel,
    DisplayModel,
    Player,
    PlayerAchievementEvent,
    PlayerChatEvent,
    PlayerCommandEvent,
    PlayerDeathEvent,
    PlayerJoinEvent,
    PlayerQuitEvent,
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
    from nonebot_plugin_mcqq.on_minecraft_msg import on_mc_msg

    mc_adapter = nonebot.get_adapter(MinecraftAdapter)

    async with app.test_matcher(on_mc_msg) as ctx:
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

        ctx.receive_event(mc_bot, player_chat_event)

        player_chat_event = PlayerChatEvent(
            **base_event,
            event_name="PlayerChatEvent",
            post_type="message",
            sub_type="player_chat",
            message=MinecraftMessage("!!This message should be ignored"),
        )

        ctx.receive_event(mc_bot, player_chat_event)

        player_command_event = PlayerCommandEvent(
            **base_event,
            event_name="PlayerCommandEvent",
            post_type="message",
            sub_type="player_command",
            command="/say Hello Command!",
        )

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

        death = DeathModel(
            key="minecraft:generic",
            args=["test_player", "Zombie"],
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
            title="minecraft:achievement.get_wood",
            frame="goal",
            description="minecraft:achievement.get_wood.desc",
        )

        achievement = AchievementModel(
            key="minecraft:achievement.get_wood",
            display=display,
            text="Player has earned the achievement [Getting Wood]",
        )

        player_achievement_event = PlayerAchievementEvent(
            **base_event,
            event_name="PlayerAchievementEvent",
            post_type="notice",
            sub_type="player_achievement",
            achievement=achievement,
        )
        ctx.receive_event(mc_bot, player_achievement_event)
