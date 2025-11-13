from nonebot import on_message, on_notice
from nonebot.adapters.minecraft import (
    PlayerAchievementEvent,
    PlayerChatEvent,
    PlayerDeathEvent,
    PlayerJoinEvent,
    PlayerQuitEvent,
)

from .config import plugin_config
from .utils.rule import mc_msg_rule
from .utils.send_to_qq import send_mc_msg_to_qq

on_mc_msg = on_message(priority=5, rule=mc_msg_rule)

on_mc_notice = on_notice(priority=4, rule=mc_msg_rule)


@on_mc_msg.handle()
async def handle_mc_msg(event: PlayerChatEvent):
    msg_text = event.player.nickname + plugin_config.say_way + str(event.message)
    if msg_text.startswith("!!"):
        return
    await send_mc_msg_to_qq(event.server_name, msg_text)


@on_mc_notice.handle()
async def handle_mc_death(event: PlayerDeathEvent):
    await send_mc_msg_to_qq(
        event.server_name,
        event.death.text or f"{event.player.nickname} 死亡了",
    )


@on_mc_notice.handle()
async def handle_mc_notice(event: PlayerJoinEvent):
    await send_mc_msg_to_qq(event.server_name, f"{event.player.nickname} 加入了游戏")


@on_mc_notice.handle()
async def handle_mc_quit(event: PlayerQuitEvent):
    await send_mc_msg_to_qq(event.server_name, f"{event.player.nickname} 离开了游戏")


@on_mc_notice.handle()
async def handle_mc_otherevent(event: PlayerAchievementEvent):
    await send_mc_msg_to_qq(
        event.server_name,
        event.achievement.text
        or f"{event.player.nickname} 获得了成就({event.achievement.key})",
    )
