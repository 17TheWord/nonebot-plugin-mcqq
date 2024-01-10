from typing import Union

from nonebot import on_message, on_notice, logger
from nonebot.adapters.minecraft import BaseChatEvent, BaseJoinEvent, BaseQuitEvent, BaseDeathEvent
from nonebot.exception import FinishedException

from mcqq_tool.rule import mc_msg_rule
from mcqq_tool.send_to_qq import send_mc_msg_to_qq

on_mc_msg = on_message(priority=5, rule=mc_msg_rule)

on_mc_notice = on_notice(priority=4, rule=mc_msg_rule)


@on_mc_msg.handle()
async def handle_mc_msg(event: BaseChatEvent):
    msg_result = f"{event.player.nickname} 说：{event.message}"
    await send_mc_msg_to_qq(event.server_name, msg_result)


@on_mc_notice.handle()
async def handle_mc_notice(event: Union[BaseJoinEvent, BaseQuitEvent, BaseDeathEvent]):
    msg_result = ""
    if isinstance(event, BaseJoinEvent):
        msg_result += f"{event.player.nickname} 加入了游戏"
    elif isinstance(event, BaseQuitEvent):
        msg_result += f"{event.player.nickname} 退出了游戏"
    elif isinstance(event, BaseDeathEvent):
        msg_result += f"{event.player.nickname} 死了"
    else:
        logger.warning(f"[MC_QQ]丨未知的事件类型: {type(event)}，无法转发")
        raise FinishedException

    await send_mc_msg_to_qq(event.server_name, msg_result)
