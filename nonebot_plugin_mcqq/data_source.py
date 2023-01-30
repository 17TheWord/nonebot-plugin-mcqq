import json
import websockets
from nonebot import get_bot, logger
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot_plugin_guild_patch import GuildMessageEvent

from typing import Union
from .utils import (
    get_mc_qq_ws_ip,
    get_mc_qq_ws_port,
    msg_process,
    send_msg_to_qq,
    mc_qq_servers_list
)

CLIENTS = []
"""客户端列表"""


async def ws_client(websocket):
    """WebSocket"""
    try:
        server_name = websocket.request_headers["x-self-name"].encode('utf-8').decode('unicode_escape')
    except KeyError:
        server_name = ""
    # 服务器名为空
    if not server_name:
        logger.error("[MC_QQ]丨未获取到该服务器的名称，连接断开")
        await websocket.close(1008, "[MC_QQ]丨未获取到该服务器的名称，连接断开")
        return
    else:
        for client in CLIENTS:
            # 重复连接
            if server_name == client["server_name"]:
                logger.error(f"[MC_QQ]丨[Server:{server_name}] 已连接至 WebSocket 服务器，无需重复连接")
                await websocket.close(1008, f"[MC_QQ]丨[Server:{server_name}] 已连接至 WebSocket 服务器，无需重复连接")
                return

        CLIENTS.append({"server_name": server_name, "ws_client": websocket})
        logger.success(f"[MC_QQ]丨[Server:{server_name}] 已连接至 WebSocket 服务器")
        try:
            async for message in websocket:
                await send_msg_to_qq(bot=get_bot(), json_msg=json.loads(message))
        except websockets.WebSocketException:
            # 移除当前客户端
            CLIENTS.remove({"server_name": server_name, "ws_client": websocket})
        if websocket.closed:
            CLIENTS.remove({"server_name": server_name, "ws_client": websocket})
            logger.error(f"[MC_QQ]丨[Server:{server_name}] 的 WebSocket 连接已断开")


async def start_ws_server():
    """启动 WebSocket 服务器"""
    global ws
    ws = await websockets.serve(ws_client, get_mc_qq_ws_ip(), get_mc_qq_ws_port())
    logger.success("[MC_QQ]丨WebSocket 服务器已开启")


async def stop_ws_server():
    """关闭 WebSocket 服务器"""
    global ws
    ws.close()
    logger.success("[MC_QQ]丨WebSocket 服务器已关闭")


async def send_msg_to_mc(bot: Bot, event: Union[GroupMessageEvent, GuildMessageEvent]):
    """发送消息到 MC"""
    # 处理来自QQ的消息
    text_msg, msgJson = await msg_process(bot=bot, event=event)
    if client_list := await get_clients(event=event):
        for client in client_list:
            if client and client['ws_client']:
                try:
                    await client['ws_client'].send(msgJson)
                    logger.success(f"[MC_QQ]丨发送至 [server:{client['server_name']}] 的消息 \"{text_msg}\"")
                except websockets.WebSocketException:
                    logger.error(f"[MC_QQ]丨发送至 [Server:{client['server_name']}] 的过程中出现了错误")
                    CLIENTS.remove(client)


async def get_clients(event: Union[GroupMessageEvent, GuildMessageEvent]) -> list:
    """获取 服务器名、ws客户端, 返回client列表"""
    res = []
    for per_client in CLIENTS:
        for per_server in mc_qq_servers_list:
            # 如果 服务器名 == ws客户端中记录的服务器名，且ws客户端存在
            if per_server['server_name'] == per_client['server_name'] and per_client['ws_client'] and (
                    per_client not in res):
                if isinstance(event, GroupMessageEvent):
                    if event.group_id in per_server['group_list']:
                        res.append(per_client)
                if isinstance(event, GuildMessageEvent):
                    if {"guild_id": event.guild_id, "channel_id": event.channel_id} in per_server['guild_list']:
                        res.append(per_client)
    return res
