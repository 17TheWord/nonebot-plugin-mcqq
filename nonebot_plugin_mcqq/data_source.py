from aiomcrcon import Client as RconClient
from mcqq_tool.utils.parse import send_msg_from_mc_common
from mcqq_tool.config import Client, CLIENTS, plugin_config
from mcqq_tool.utils import rcon_connect
from mcqq_tool.utils.send.send_common import remove_client
from nonebot import logger
from nonebot.drivers import URL, ASGIMixin, WebSocketServerSetup
from nonebot.drivers.websockets import WebSocket, WebSocketClosed


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
        for per_server_name, server in plugin_config.mc_qq_server_dict.items():
            if server_name == per_server_name:
                if server.rcon_msg or server.rcon_cmd:
                    rcon_client = RconClient(
                        websocket.__dict__["websocket"].__dict__["scope"]["client"][0],
                        server.rcon_port,
                        server.rcon_password
                    )
                    await rcon_connect(rcon_client=rcon_client, server_name=server_name)
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
                message = await websocket.receive()
                await send_msg_from_mc_common(message=message)

        except WebSocketClosed as e:
            logger.warning(f"[MC_QQ]丨[Server:{server_name}] 的 WebSocket 出现异常：{e}")
        finally:
            await remove_client(server_name=server_name)


async def set_route(driver: ASGIMixin):
    driver.setup_websocket_server(
        WebSocketServerSetup(
            path=URL(plugin_config.mc_qq_ws_url),
            name="mcqq",
            handle_func=_ws_handler,
        )
    )
    logger.success(f"[MC_QQ]丨WebSocket 服务器已启动，路由：{plugin_config.mc_qq_ws_url}")
