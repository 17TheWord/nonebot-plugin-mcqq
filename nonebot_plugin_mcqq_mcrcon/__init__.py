from typing import Union

from nonebot import get_driver, on_command, on_message
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, GROUP_OWNER, GROUP_ADMIN
from nonebot.permission import SUPERUSER

from .data_source import (
    send_msg_to_mc,
    send_command_to_mc,
    start_ws_server,
    stop_ws_server
)
from .utils import msg_rule, GUILD_ADMIN, GuildMessageEvent

mc_qq_mcrcon = on_message(priority=5, rule=msg_rule, block=False)

mc_qq_mcrcon_command = on_command(
    "mcc",
    priority=3,
    rule=msg_rule,
    permission=SUPERUSER | GROUP_OWNER | GROUP_ADMIN | GUILD_ADMIN,
    block=True
)

driver = get_driver()


# Bot 连接时
@driver.on_bot_connect
async def on_start():
    # 启动 WebSocket 服务器
    await start_ws_server()


# Bot 断开连接时
@driver.on_bot_disconnect
async def on_close():
    # 关闭 WebSocket 服务器
    await stop_ws_server()


# 收到 群/频道 消息时
@mc_qq_mcrcon.handle()
async def handle_first_receive(bot: Bot, event: Union[GroupMessageEvent, GuildMessageEvent]):
    await send_msg_to_mc(bot=bot, event=event)


# 收到 群/频道 命令时
@mc_qq_mcrcon_command.handle()
async def handle_first_receive(bot: Bot, event: Union[GroupMessageEvent, GuildMessageEvent]):
    await send_command_to_mc(bot=bot, event=event)
