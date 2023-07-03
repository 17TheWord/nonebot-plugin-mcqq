from aiomcrcon import Client as RconClient
from nonebot import logger, get_bot
from nonebot.drivers import URL, ReverseDriver, WebSocketServerSetup
from nonebot.drivers.websockets import WebSocket, WebSocketClosed

from mcqq_tool.common import plugin_config
from mcqq_tool.config import Client, CLIENTS
from mcqq_tool.utils import send_msg_to_qq, rcon_connect, remove_client


async def _ws_handler(websocket: WebSocket):
    """WebSocket"""
    try:
        server_name = websocket.request.headers.get("x-self-name").encode('utf-8').decode('unicode_escape')
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
        bot_self_id = None
        for server in plugin_config.mc_qq_server_list:
            if server_name == server.server_name:
                if server.rcon_enable:
                    rcon_client = RconClient(
                        websocket.__dict__["websocket"].__dict__["scope"]["client"][0],
                        plugin_config.mc_qq_rcon_dict[server_name],
                        plugin_config.mc_qq_rcon_password
                    )
                    await rcon_connect(rcon_client=rcon_client, server_name=server_name)
                    bot_self_id = str(server.self_id) if server.self_id else None
                    break
        CLIENTS[server_name] = Client(
            server_name=server_name,
            websocket=websocket,
            rcon=rcon_client
        )

        await websocket.accept()

        logger.success(f"[MC_QQ]丨[Server:{server_name}] 已连接至 WebSocket 服务器")

        try:
            while True:
                try:
                    message = await websocket.receive()
                    # 获取指定ID Bot
                    bot = get_bot(bot_self_id)
                except KeyError as e:
                    logger.warning(f"[MC_QQ]丨[Server:{server_name}] 对应 self_id 的 Bot 不存在：{e}")
                except ValueError as e:
                    logger.warning(f"[MC_QQ]丨[Server:{server_name}] 未指定Bot，且当前无其他Bot可用：{e}")
                else:
                    # 以指定ID Bot 发送消息
                    await send_msg_to_qq(bot=bot, message=message)

        except WebSocketClosed as e:
            logger.warning(f"[MC_QQ]丨[Server:{server_name}] 的 WebSocket 出现异常：{e}")
        finally:
            await remove_client(server_name=server_name)


async def set_route(driver: ReverseDriver):
    driver.setup_websocket_server(
        WebSocketServerSetup(
            path=URL(plugin_config.mc_qq_ws_url),
            name="mcqq",
            handle_func=_ws_handler,
        )
    )
    logger.success(f"[MC_QQ]丨WebSocket 服务器已启动，路由：{plugin_config.mc_qq_ws_url}")
