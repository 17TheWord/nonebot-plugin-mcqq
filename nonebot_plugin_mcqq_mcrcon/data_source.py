import json
import mcrcon
import websockets

from nonebot import logger, get_bot
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot
from nonebot_plugin_guild_patch import GuildMessageEvent

from typing import Union
from .utils import (
    send_msg_to_qq,
    get_mc_qq_ws_ip,
    get_mc_qq_ws_port,
    get_mc_qq_mcrcon_password,
    msg_process,
    mc_qq_servers_list,
    mc_qq_mcrcon_rcon_list,
)

CLIENTS = []
"""客户端列表"""


async def ws_client(websocket):
    """WebSocket"""
    mcrcon_connect = None
    try:
        server_name = websocket.request_headers["x-self-name"].encode('utf-8').decode('unicode_escape')
    except KeyError:
        server_name = ""
    if not server_name:
        logger.error("[MC_QQ]丨未获取到该服务器的名称")
        await websocket.close(1008, "[MC_QQ]丨未获取到该服务器的名称")
    else:
        for client in CLIENTS:
            if server_name == client["server_name"]:
                logger.error(f"[MC_QQ]丨[Server:{server_name}] 已连接至WebSocket服务器，无需重复连接。")
                await websocket.close(1008, f"[MC_QQ]丨[Server:{server_name}] 已连接至WebSocket服务器，无需重复连接。")
        try:
            mcrcon_connect = mcrcon.MCRcon(
                websocket.remote_address[0],
                get_mc_qq_mcrcon_password(),
                mc_qq_mcrcon_rcon_list[server_name]
            )
            mcrcon_connect.connect()
            logger.success(f"[MC_QQ_Rcon]丨[Server:{server_name}] 的 Rcon 已连接")
        except KeyError:
            logger.error(f"[MC_QQ_Rcon]丨[Server:{server_name}] 的 Rcon 端口未获取")

        CLIENTS.append(
            {"server_name": server_name, "ws_client": websocket, "mcrcon_connect": mcrcon_connect}
        )
        logger.success(f"[MC_QQ_Rcon]丨[Server:{server_name}] 已连接至 WebSocket 服务器")

    try:
        async for message in websocket:
            await send_msg_to_qq(bot=get_bot(), json_msg=json.loads(message))
    except websockets.WebSocketException:
        CLIENTS.remove({"server_name": server_name, "ws_client": websocket, "mcrcon_connect": mcrcon_connect})
    except ConnectionRefusedError:
        logger.error(f"[MC_QQ_Rcon]丨[Server:{server_name}] 的 Rcon 未开启或连接信息错误")
        logger.error(f"[MC_QQ_Rcon]丨[Server:{server_name}] 的 WebSocket 连接已断开")
    if websocket.closed:
        mcrcon_connect.disconnect()
        CLIENTS.remove({"server_name": server_name, "ws_client": websocket, "mcrcon_connect": mcrcon_connect})
        logger.error(f"[MC_QQ_Rcon]丨[Server:{server_name}] 的 WebSocket、Rcon 连接已断开")


async def start_ws_server():
    """启动 WebSocket 服务器"""
    global ws
    ws = await websockets.serve(ws_client, get_mc_qq_ws_ip(), get_mc_qq_ws_port())
    logger.success("[MC_QQ_Rcon]丨WebSocket 服务器已开启")


async def stop_ws_server():
    """关闭 WebSocket 服务器"""
    global ws
    ws.close()
    logger.success("[MC_QQ_Rcon]丨WebSocket 服务器已关闭")


async def send_msg_to_mc(bot: Bot, event: Union[GroupMessageEvent, GuildMessageEvent]):
    """发送消息到 Minecraft"""
    text_msg, command_msg = await msg_process(bot=bot, event=event)
    if client_list := await get_clients(event=event):
        for client in client_list:
            if client and client['mcrcon_connect']:
                try:
                    client['mcrcon_connect'].command(command_msg)
                    logger.success(f"[MC_QQ_Rcon]丨发送至 [server:{client['server_name']}] 的消息 \"{text_msg}\"")
                except mcrcon.MCRconException:
                    logger.error(f"[MC_QQ_Rcon]丨发送至 [Server:{client['server_name']}] 的过程中出现了错误")
                    # 连接关闭则移除客户端
                    CLIENTS.remove(client)


async def send_command_to_mc(bot: Bot, event: Union[GroupMessageEvent, GuildMessageEvent]):
    """发送命令到 Minecraft"""
    if client_list := await get_clients(event=event):
        for client in client_list:
            if client and client['mcrcon_connect']:
                try:
                    await bot.send(event, message=client['mcrcon_connect'].command(event.raw_message.strip("/mcc")))
                    logger.success(
                        f"[MC_QQ_Rcon]丨发送至 [server:{client['server_name']}] 的命令 \"{event.raw_message.strip('/mcc')}\""
                    )
                except mcrcon.MCRconException:
                    logger.error(f"[MC_QQ_Rcon]丨发送至 [Server:{client['server_name']}] 的过程中出现了错误")
                    # 连接关闭则移除客户端
                    CLIENTS.remove(client)


async def get_clients(event: Union[GroupMessageEvent, GuildMessageEvent]):
    """获取 服务器名、ws客户端、Rcon连接"""
    res = []
    for per_client in CLIENTS:
        for per_server in mc_qq_servers_list:
            # 如果 服务器名 == ws客户端中记录的服务器名，且ws客户端存在
            if per_server['server_name'] == per_client['server_name'] and per_client['ws_client']:
                if isinstance(event, GroupMessageEvent):
                    if event.group_id in per_server['group_list']:
                        res.append(per_client)
                if isinstance(event, GuildMessageEvent):
                    if {"guild_id": event.guild_id, "channel_id": event.channel_id} in per_server['guild_list']:
                        res.append(per_client)
    return res
