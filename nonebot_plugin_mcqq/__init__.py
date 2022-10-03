from nonebot import on_message
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot import get_driver
from nonebot_plugin_guild_patch import GuildMessageEvent

from .data_source import send_msg_to_mc, on_connect
from .utils import get_mc_qq_group_list, get_mc_qq_guild_list

mc_qq = on_message(priority=5)
driver = get_driver()


# bot连接时
@driver.on_bot_connect
async def on_start(bot: Bot):
    # 循环尝试连接
    while True:
        await on_connect(bot=bot)
        if not OSError:
            break


# 收到 群/频 道消息时
@mc_qq.handle()
async def handle_first_receive(bot: Bot, event: GroupMessageEvent | GuildMessageEvent):
    if event.message_type == "group":
        if event.group_id in get_mc_qq_group_list(bot=bot):
            await send_msg_to_mc(bot=bot, event=event)
    elif event.message_type == "guild":
        for per_channel in get_mc_qq_guild_list(bot=bot):
            if event.guild_id == per_channel[0] and event.channel_id == per_channel[1]:
                await send_msg_to_mc(bot=bot, event=event)
