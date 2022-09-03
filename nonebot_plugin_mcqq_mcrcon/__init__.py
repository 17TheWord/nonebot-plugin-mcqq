from nonebot import get_driver
from nonebot import on_message
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent

from nonebot_plugin_guild_patch import GuildMessageEvent
from .data_source import send_msg_to_mc, on_mcrcon_connect, on_connect, mcr, group_list

mc_qq_mcrcon = on_message(priority=5)

driver = get_driver()


# Bot 连接时
@driver.on_bot_connect
async def do_something(bot: Bot):
    while True:
        await on_mcrcon_connect()
        await on_connect(bot=bot)
        if not OSError:
            break


# 断开连接时
@driver.on_shutdown
async def do_something():
    mcr.disconnect()


# 收到 群/频 道消息时
@mc_qq_mcrcon.handle()
async def handle_first_receive(bot: Bot, event: GuildMessageEvent | GroupMessageEvent):
    if isinstance(event, GroupMessageEvent):
        if event.group_id in group_list['group_list']:
            await send_msg_to_mc(bot=bot, event=event)
    elif isinstance(event, GuildMessageEvent):
        for per_channel in group_list['guild_list']:
            if event.guild_id == per_channel['guild_id'] and event.channel_id == per_channel['channel_id']:
                await send_msg_to_mc(bot=bot, event=event)
