from nonebot import on_message, get_driver, on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageEvent, Message
from nonebot_plugin_guild_patch import GuildMessageEvent
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER

from .data_source import send_msg_to_mc, start_ws_server, stop_ws_server
from .utils import msg_rule,create_config_file,get_config,set_config
from typing import Union

import json

mc_qq = on_message(priority=5, rule=msg_rule, block=False)
set_mcqq_ip=on_command("mcqq 设置ip", priority=7,permission=SUPERUSER)
set_mcqq_port=on_command("mcqq 设置端口", priority=7,permission=SUPERUSER)
set_mcqq_send_group_name=on_command("mcqq 设置是否发送群名", priority=7,permission=SUPERUSER)
set_mcqq_display_server_name=on_command("mcqq 设置是否显示服务器名", priority=7,permission=SUPERUSER)

driver = get_driver()

create_config_file()
# bot连接时
@driver.on_bot_connect
async def on_start():
    # 启动 WebSocket 服务器
    await start_ws_server()


@driver.on_bot_disconnect
async def on_close():
    # 关闭 WebSocket 服务器
    await stop_ws_server()


# 收到 群/频 道消息时
@mc_qq.handle()
async def handle_first_receive(bot: Bot, event: Union[GroupMessageEvent, GuildMessageEvent]):
    await send_msg_to_mc(bot=bot, event=event)


@set_mcqq_ip.handle()
async def _(bot: Bot, event: MessageEvent, arg: Message=CommandArg()):
    arg = arg.extract_plain_text()
    config_json=get_config()
    config_json["mcqq_ws_ip"]=arg
    set_config(json.dumps(config_json,indent=4))
    await set_mcqq_ip.finish("完成")
@set_mcqq_port.handle()
async def _(bot: Bot, event: MessageEvent, arg: Message=CommandArg()):
    arg = arg.extract_plain_text()
    config_json=get_config()
    config_json["mcqq_ws_port"]=int(arg)
    set_config(json.dumps(config_json,indent=4))
    await set_mcqq_port.finish("完成")
@set_mcqq_send_group_name.handle()
async def _(bot: Bot, event: MessageEvent, arg: Message=CommandArg()):
    arg = arg.extract_plain_text()
    b=True
    if arg=="开" or "on" or "true":
        b=True
    elif arg=="关" or "off" or "false":
        b=False
    config_json=get_config()
    config_json["mcqq_send_group_name"]=b
    set_config(json.dumps(config_json,indent=4))
    await set_mcqq_send_group_name.finish("完成")
@set_mcqq_display_server_name.handle()
async def _(bot: Bot, event: MessageEvent, arg: Message=CommandArg()):
    arg = arg.extract_plain_text()
    b=True
    if arg=="开" or "on" or "true":
        b=True
    elif arg=="关" or "off" or "false":
        b=False
    config_json=get_config()
    config_json["mcqq_display_server_name"]=b
    set_config(json.dumps(config_json,indent=4))
    await set_mcqq_display_server_name.finish("完成")