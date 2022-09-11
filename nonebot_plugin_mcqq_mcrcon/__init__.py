from nonebot import get_driver
from nonebot import on_message
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent

from nonebot_plugin_guild_patch import GuildMessageEvent
from .data_source import send_msg_to_mc, on_mcrcon_connect, on_connect, dis_mcrcon_connect
from .utils import get_mc_qq_group_list, get_mc_qq_guild_list

mc_qq_mcrcon = on_message(priority=5)

driver = get_driver()


# Bot 连接时
@driver.on_bot_connect
async def on_start(bot: Bot):
    while True:
        on_mcrcon_connect(bot=bot)
        await on_connect(bot=bot)
        if not OSError:
            break


# 断开连接时
@driver.on_shutdown
async def on_stop():
    dis_mcrcon_connect()


# 收到 群/频 道消息时
@mc_qq_mcrcon.handle()
async def handle_first_receive(bot: Bot, event: GuildMessageEvent | GroupMessageEvent):
    if isinstance(event, GroupMessageEvent):
        if event.group_id in get_mc_qq_group_list(bot=bot):
            await send_msg_to_mc(bot=bot, event=event)
    elif isinstance(event, GuildMessageEvent):
        for per_channel in get_mc_qq_guild_list(bot=bot):
            if event.guild_id == per_channel[0] and event.channel_id == per_channel[1]:
                await send_msg_to_mc(bot=bot, event=event)
