from nonebot import get_driver
from nonebot import on_message
from nonebot.adapters.onebot.v11 import Bot

from .data_source import *

mc_qq = on_message(priority=5)

driver = get_driver()


# Bot 连接时
# TODO 连接失败则重新尝试
@driver.on_bot_connect
async def do_something():
    try:
        mcr.connect()
    except ConnectionRefusedError:
        nonebot.logger.error("[MC_QQ]丨连接 MCRcon 失败！")


# 断开连接时
@driver.on_shutdown
async def do_something():
    mcr.disconnect()


# 收到 群/频 道消息时
@mc_qq.handle()
async def handle_first_receive(bot: Bot, event: GuildMessageEvent | GroupMessageEvent):
    await send_msg_to_mc(bot, event)
