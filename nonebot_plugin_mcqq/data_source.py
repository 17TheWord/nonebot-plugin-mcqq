import aiomcrcon
import websockets
from mcqq_tool.config import Client, CLIENTS
from mcqq_tool.utils import send_msg_to_qq, remove_client, rcon_connect
from nonebot import logger, get_bot

from .utils import plugin_config


async def ws_client(websocket: websockets.WebSocketServerProtocol):
    """WebSocket"""
    try:
        server_name = websocket.request_headers["x-self-name"].encode('utf-8').decode('unicode_escape')
    except KeyError as e:
        # 服务器名为空
        logger.error(f"[MC_QQ]丨未获取到该服务器的名称，连接断开：{e}")
        await websocket.close(1008, "[MC_QQ]丨未获取到该服务器的名称，连接断开")
        return
    else:

        if CLIENTS.get(server_name):
            # 服务器名已存在
            logger.error(f"[MC_QQ]丨已有相同服务器名的连接，连接断开")
            await websocket.close(1008, "[MC_QQ]丨已有相同服务器名的连接")
            return

        rcon_client = None
        bot_id = ""
        for server in plugin_config.mc_qq_server_list:
            if server_name == server.server_name:
                bot_id = str(server.self_id)
                if server.rcon_enable:
                    rcon_client = aiomcrcon.Client(
                        websocket.remote_address[0],
                        plugin_config.mc_qq_rcon_dict[server_name],
                        plugin_config.mc_qq_rcon_password
                    )
                    await rcon_connect(rcon_client=rcon_client, server_name=server_name)
                    break
        CLIENTS[server_name] = Client(
            server_name=server_name,
            websocket=websocket,
            rcon=rcon_client
        )
        logger.success(f"[MC_QQ]丨[Server:{server_name}] 已连接至 WebSocket 服务器")

        try:
            async for message in websocket:
                try:
                    # 获取指定ID Bot
                    bot = get_bot(bot_id)
                except KeyError as e:
                    logger.error(f"[MC_QQ]丨[Server:{server_name}] 的 Bot 未获取，将尝试使用其他Bot发送消息：{e}")
                    try:
                        # 获取可用 Bot
                        bot = get_bot()
                    except ValueError as e:
                        logger.error(f"[MC_QQ]丨[Server:{server_name}] 没有可用的 Bot，无法发送消息：{e}")
                    else:
                        # 以可用 Bot 发送消息
                        # 如果 Bot 未在指定群聊，则会报错
                        await send_msg_to_qq(bot=bot, message=message)
                else:
                    # 以指定ID Bot 发送消息
                    await send_msg_to_qq(bot=bot, message=message)

        except websockets.WebSocketException as e:
            logger.error(f"[MC_QQ]丨[Server:{server_name}] 的 WebSocket 出现异常：{e}")
        finally:
            if websocket.closed:
                logger.error(f"[MC_QQ]丨[Server:{server_name}] 的 WebSocket 连接已断开")
            await remove_client(server_name=server_name)


async def start_ws_server():
    """启动 WebSocket 服务器"""
    global ws
    ws = await websockets.serve(ws_client, plugin_config.mc_qq_ws_ip, plugin_config.mc_qq_ws_port)
    logger.success(f"[MC_QQ]丨WebSocket 服务器已在 {plugin_config.mc_qq_ws_ip}:{plugin_config.mc_qq_ws_port} 已开启")


async def stop_ws_server():
    """关闭 WebSocket 服务器"""
    global ws
    ws.close()
    logger.success("[MC_QQ]丨WebSocket 服务器已关闭")
