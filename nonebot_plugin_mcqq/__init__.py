from typing import Union

from mcqq_tool import GUILD_ADMIN
from nonebot import on_message, on_command, get_driver
from nonebot.adapters import Message
from nonebot.exception import FinishedException
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, GROUP_ADMIN, GROUP_OWNER
from nonebot.permission import SUPERUSER
from nonebot_plugin_guild_patch import GuildMessageEvent
from mcqq_tool.utils import send_msg_to_mc, send_cmd_to_mc
from .data_source import start_ws_server, stop_ws_server
from .utils import msg_rule

mc_qq = on_message(priority=2, rule=msg_rule)

mc_qq_cmd = on_command("minecraft_command", aliases={"mcc"}, priority=1, rule=msg_rule, block=True)

driver = get_driver()


# bot连接时
@driver.on_bot_connect
async def on_start():
    # 启动 WebSocket 服务器
    await start_ws_server()


@driver.on_bot_disconnect
async def on_close():
    # 关闭 WebSocket 服务器
    await stop_ws_server()


# 收到消息时
@mc_qq.handle()
async def handle_msg(bot: Bot, event: Union[GroupMessageEvent, GuildMessageEvent]):
    await send_msg_to_mc(bot=bot, event=event)


# 收到命令时
@mc_qq_cmd.handle()
async def handle_cmd(bot: Bot, event: Union[GroupMessageEvent, GuildMessageEvent], args: Message = CommandArg()):
    if isinstance(event, GroupMessageEvent):
        if not await (GROUP_ADMIN | GROUP_OWNER | SUPERUSER)(bot, event):
            await mc_qq_cmd.finish("你没有权限使用此命令")
    elif isinstance(event, GuildMessageEvent):
        if not await (GUILD_ADMIN | SUPERUSER)(bot, event):
            await mc_qq_cmd.finish("你没有权限使用此命令")
    await send_cmd_to_mc(bot=bot, event=event, cmd=args.extract_plain_text())
