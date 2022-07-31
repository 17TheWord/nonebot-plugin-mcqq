import re

import nonebot
import websockets

from src.msg_qq_config import group_list

# 要替换的 CQ 码
cq_type = {
    "face": "表情",
    "record": "语音",
    "video": "短视频",
    "at": "@",
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
async def on_connect(url: str, bot):
    # 全局变量 websocket
    global websocket

    # 建立链接
    try:
        async with websockets.connect(url) as websocket:
            while True:
                # 后台日志
                nonebot.logger.success("[Msq_QQ]丨已成功连接到 Msq_QQ WebSocket 服务器！")
                # 接收消息赋值
                recv_msg = await websocket.recv()
                if group_list['group_list']:
                    for per_group in group_list['group_list']:
                        await bot.call_api("send_group_msg", group_id=per_group, message=recv_msg)
                if group_list['guild_list']:
                    for per_guild in group_list['guild_list']:
                        await bot.call_api("send_guild_channel_msg", guild_id=per_guild['guild_id'],
                                           channel_id=per_guild['channel_id'], message=recv_msg)
                nonebot.logger.success("[Msg_QQ]丨发送消息：" + recv_msg)
    except (OSError, websockets.exceptions.ConnectionClosedError, websockets.exceptions.ConnectionClosedOK) as e:
        nonebot.logger.error("[Msq_QQ]：无法连接到 WebSocket 服务器，正在重新连接。")
        await on_connect(url=url, bot=bot)


async def send_msg_to_mc(event):
    get_msg = event.raw_message

    # 拼接信息类型
    final_msg = re.sub(r'\[CQ.*\]', "", get_msg)
    msg_type_list = re.findall(r'CQ:(.+?),', get_msg)

    temp_str = ""
    for msg_type in msg_type_list:
        temp_str += f"[{cq_type[msg_type]}]"

    final_msg += temp_str
    await websocket.send(f"{event.sender.nickname} 说：{final_msg}")
    nonebot.logger.success(f"[Msq_QQ]丨发送到 MC 服务器：{event.sender.nickname} 说：{final_msg}")
