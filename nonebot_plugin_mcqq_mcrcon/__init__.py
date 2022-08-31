from nonebot import get_driver
from nonebot import on_message
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent

from nonebot_plugin_guild_patch import GuildMessageEvent
from .data_source import send_msg_to_mc, on_mcrcon_connect, on_connect, mcr
from src.mc_qq_config import ws_url

mc_qq = on_message(priority=5)

driver = get_driver()


# Bot 连接时
# TODO 连接失败则重新尝试
@driver.on_bot_connect
async def do_something(bot: Bot):
    while True:
        await on_mcrcon_connect()
        await on_connect(ws_url, bot=bot)
        if not OSError:
            break


# 断开连接时
@driver.on_shutdown
async def do_something():
    mcr.disconnect()


# 收到 群/频 道消息时
@mc_qq.handle()
async def handle_first_receive(bot: Bot, event: GuildMessageEvent | GroupMessageEvent):
    await send_msg_to_mc(bot, event)
