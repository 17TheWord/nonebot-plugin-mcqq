from nonebot import on_message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot, MessageEvent
from nonebot import get_driver
from ..nonebot_plugin_guild_patch import GuildMessageEvent

from .data_source import *
from src.msg_qq_config import ws_url, group_list

msg_qq = on_message(priority=5)
driver = get_driver()


# bot连接时
@driver.on_bot_connect
async def on_open(bot: Bot):
    # 循环尝试连接
    while True:
        await on_connect(ws_url, bot=bot)
        if not OSError:
            break


# 收到 群/频 道消息时
@msg_qq.handle()
async def handle_first_receive(event: MessageEvent):
    if isinstance(event, GroupMessageEvent):
        if event.group_id in group_list['group_list']:
            await send_msg_to_mc(event=event)
    elif isinstance(event, GuildMessageEvent):
        for per_channel in group_list['guild_list']:
            if event.guild_id == per_channel['guild_id'] and event.channel_id == per_channel['channel_id']:
                await send_msg_to_mc(event=event)
