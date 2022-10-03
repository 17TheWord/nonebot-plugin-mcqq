import nonebot
import websockets

from .utils import *

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
    url = f"ws://{get_mc_qq_ip(bot=bot)}:{get_mc_qq_ws_port(bot=bot)}"
    # 建立链接
    try:
        async with websockets.connect(url) as websocket:
            nonebot.logger.success("[MC_QQ]丨已成功连接到 MC_QQ WebSocket 服务器！")
            while True:
                # 接收消息赋值
                recv_msg = await websocket.recv()
                # 发送消息
                await send_msg_to_qq(bot=bot, recv_msg=recv_msg)
                # 后台日志
                nonebot.logger.success("[MC_QQ]丨发送消息到QQ ：" + recv_msg)
    except (OSError, websockets.exceptions.ConnectionClosedError, websockets.exceptions.ConnectionClosedOK):
        nonebot.logger.error("[MC_QQ]：无法连接到 MC_QQ WebSocket 服务器，正在重新连接。")
        await on_connect(bot=bot)


async def send_msg_to_mc(bot: Bot, event):
    text_msg, msgJson = await msg_process(bot=bot, event=event)
    await websocket.send(msgJson)
    nonebot.logger.success(f"[MC_QQ]丨来自QQ的消息：" + text_msg)
