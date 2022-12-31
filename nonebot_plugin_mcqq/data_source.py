import json

import websockets
from nonebot import get_bot, logger
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot_plugin_guild_patch import GuildMessageEvent

from .utils import get_mc_qq_ip, get_mc_qq_ws_port, msg_process, send_msg_to_qq, get_mc_qq_servers_list

CLIENTS = []


async def echo(websocket):
    try:
        async for message in websocket:
            msg = json.loads(message)
            if msg['event_name'] == "ConnectEvent":
                CLIENTS.append([msg['server_name'], websocket])
                logger.success(f"[MC_QQ]丨MC服务器 {msg['server_name']} 已连接至 WebSocket 服务器")
            # 发送消息到QQ
            else:
                await send_msg_to_qq(bot=get_bot(), recv_msg=message)
    except:
        CLIENTS.remove([msg['server_name'], websocket])
        logger.error(f"[MC_QQ]丨MC服务器 {msg['server_name']} 的 WebSocket 连接已断开")
    if websocket.closed:
        logger.error(f"[MC_QQ]丨MC服务器 {msg['server_name']} 的 WebSocket 连接已断开")


# 启动 WebSocket 服务器
async def start_ws_server():
    global ws
    ws = await websockets.serve(echo, get_mc_qq_ip(), get_mc_qq_ws_port())
    logger.success("[MC_QQ]丨WebSocket 服务器已开启")


# 关闭 WebSocket 服务器
async def stop_ws_server():
    global ws
    ws.close()


# 发送消息到 MC
async def send_msg_to_mc(bot: Bot, event: GroupMessageEvent | GuildMessageEvent):
    # 处理来自QQ的消息
    text_msg, msgJson = await msg_process(bot=bot, event=event)
    for per_client in CLIENTS:
        try:
            for per_server in get_mc_qq_servers_list():
                if per_server[0] == per_client[0] and per_client[1]:
                    if event.message_type == "group":
                        if event.group_id in per_server[1]:
                            await per_client[1].send(msgJson)
                    if event.message_type == "guild":
                        if [event.guild_id, event.channel_id] in per_server[2]:
                            await per_client[1].send(msgJson)
        except websockets.WebSocketException as e:
            logger.error("[MC_QQ]丨" + e)
            # 连接关闭则移除客户端
            CLIENTS.remove(per_client)
            await send_msg_to_mc(bot, event)
            continue
        logger.success(f"[MC_QQ]丨发送到MC服务器 {per_client[0]} 的消息：\"{text_msg}\"")
