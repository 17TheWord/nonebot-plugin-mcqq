from typing import Union

from mcqq_tool.rule import mc_msg_rule
from nonebot import on_notice, on_message
from mcqq_tool.send_to_qq import send_mc_msg_to_qq
from nonebot.adapters.minecraft import (
    BaseChatEvent,
    BaseJoinEvent,
    BaseQuitEvent,
    BaseDeathEvent,
)

on_mc_msg = on_message(priority=5, rule=mc_msg_rule)

on_mc_notice = on_notice(priority=4, rule=mc_msg_rule)


@on_mc_msg.handle()
async def handle_mc_msg(event: Union[BaseChatEvent, BaseDeathEvent]):
    msg_result = str(event.message) if isinstance(event, BaseDeathEvent) else f"{event.player.nickname} 说：{event.message}"
    await send_mc_msg_to_qq(event.server_name, msg_result)


@on_mc_notice.handle()
async def handle_mc_notice(event: Union[BaseJoinEvent, BaseQuitEvent]):
    msg_result = f"{event.player.nickname} {'加入' if isinstance(event, BaseJoinEvent) else '退出'}了游戏"
    await send_mc_msg_to_qq(event.server_name, msg_result)
