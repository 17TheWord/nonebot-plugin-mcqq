from nonebot import on_message, get_driver
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot_plugin_guild_patch import GuildMessageEvent

from .data_source import send_msg_to_mc, start_ws_server, stop_ws_server
from .utils import msg_rule

mc_qq = on_message(priority=5, rule=msg_rule, block=False)

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


# 收到 群/频 道消息时
@mc_qq.handle()
async def handle_first_receive(bot: Bot, event: GroupMessageEvent | GuildMessageEvent):
    await send_msg_to_mc(bot=bot, event=event)
