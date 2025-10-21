from nonebot import on_message, on_notice
from nonebot.adapters.minecraft import (
    BaseChatEvent,
    BaseDeathEvent,
    BaseJoinEvent,
    BaseQuitEvent,
)

from .config import plugin_config
from .utils.rule import mc_msg_rule
from .utils.send_to_qq import send_mc_msg_to_qq

on_mc_msg = on_message(priority=5, rule=mc_msg_rule)

on_mc_notice = on_notice(priority=4, rule=mc_msg_rule)


@on_mc_msg.handle()
async def handle_mc_msg(event: BaseChatEvent | BaseDeathEvent):
    msg_text = str(event.message)
    if msg_text.startswith("!!"):
        return
    msg_result = (
        msg_text
        if isinstance(event, BaseDeathEvent)
        else event.player.nickname + plugin_config.say_way + msg_text
    )
    await send_mc_msg_to_qq(event.server_name, msg_result)


@on_mc_notice.handle()
async def handle_mc_notice(event: BaseJoinEvent | BaseQuitEvent):
    msg_result = f"{event.player.nickname} {'加入' if isinstance(event, BaseJoinEvent) else '退出'}了游戏"
    await send_mc_msg_to_qq(event.server_name, msg_result)
