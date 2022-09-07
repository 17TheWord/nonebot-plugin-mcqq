import re

import nonebot
import websockets
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot_plugin_guild_patch import GuildMessageEvent

from src.mc_qq_config import group_list, mc_ip, ws_port

# 要替换的 CQ 码
msg_type = {
    "face": "表情",
    "record": "语音",
    "video": "短视频",
    "rps": "猜拳",
    "dice": "骰子",
    "anonymous": "匿名消息",
    "share": "链接分享",
    "contact": "推荐好友/群",
    "location": "位置",
    "music": "音乐",
    "image": "图片",
    "reply": "回复",
    "redbag": "红包",
    "poke": "戳一戳",
    "gift": "礼物",
    "forward": "合并转发",
    "xml": "XML",
    "json": "JSON",
    "cardimage": "大图",
}


# 连接
async def on_connect(bot):
    # 全局变量 websocket
    global websocket
    url = f"ws://{mc_ip}:{ws_port}"
    # 建立链接
    try:
        async with websockets.connect(url) as websocket:
            nonebot.logger.success("[MC_QQ]丨已成功连接到 MC_QQ WebSocket 服务器！")
            while True:
                # 后台日志
                # 接收消息赋值
                recv_msg = await websocket.recv()
                if group_list['group_list']:
                    for per_group in group_list['group_list']:
                        await bot.call_api("send_group_msg", group_id=per_group, message=recv_msg)
                if group_list['guild_list']:
                    for per_guild in group_list['guild_list']:
                        await bot.call_api("send_guild_channel_msg", guild_id=per_guild['guild_id'],
                                           channel_id=per_guild['channel_id'], message=recv_msg)
                nonebot.logger.success("[MC_QQ]丨发送消息：" + recv_msg)
    except (OSError, websockets.exceptions.ConnectionClosedError, websockets.exceptions.ConnectionClosedOK):
        nonebot.logger.error("[MC_QQ]：无法连接到 WebSocket 服务器，正在重新连接。")
        await on_connect(bot=bot)


# todo 17 改成 MessageSegment 格式解析
async def send_msg_to_mc(event, bot):
    # 初始化源消息
    final_msg = ""
    for msg in event.message:
        print(msg)
        if msg.type == "text":
            final_msg += f"{msg.data['text']} "
        elif msg.type == "at":
            final_msg += f"@{await get_member_nickname(bot, event, msg.data['qq'])} "
        else:
            final_msg += f"[{msg_type.get(msg.type, msg.type)}] "
    await websocket.send(f"{event.sender.nickname} 说：{final_msg}")
    nonebot.logger.success(f"[MC_QQ]丨发送到 MC 服务器：{event.sender.nickname} 说：{final_msg}")


# 获取群成员昵称
async def get_member_nickname(bot, event, user_id):
    # 判断从 群 或者 频道 获取成员信息
    if isinstance(event, GroupMessageEvent):
        member_info = await bot.get_group_member_info(group_id=event.group_id, user_id=user_id)
    elif isinstance(event, GuildMessageEvent):
        await bot.get_guild_member_profile(guild_id=event.guild_id, user_id=str(user_id))
    # 返回成员昵称
    return member_info['nickname']
