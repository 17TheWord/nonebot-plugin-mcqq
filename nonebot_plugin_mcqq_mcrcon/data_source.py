import time
import mcrcon
import websockets
import nonebot
from mcrcon import MCRcon
from .utils import *

global mcr


# 配置 MCRcon 连接信息
async def on_connect(bot):
    # 全局变量 websocket
    global websocket

    url = f"ws://{get_mc_qq_ip(bot=bot)}:{get_mc_qq_ws_port(bot=bot)}"

    # 建立链接
    try:
        async with websockets.connect(url) as websocket:
            nonebot.logger.success("[MC_QQ]丨已成功连接到 MC_QQ WebSocket 服务器！")
            while True:
                # 后台日志
                # 接收消息赋值
                recv_msg = await websocket.recv()
                # 发送消息到 QQ
                await send_msg_to_qq(bot=bot, recv_msg=recv_msg)
                nonebot.logger.success("[MC_QQ]丨发送消息：" + recv_msg)
    except (OSError, websockets.exceptions.ConnectionClosedError, websockets.exceptions.ConnectionClosedOK):
        nonebot.logger.error("[MC_QQ]丨无法连接到 MC_QQ WebSocket 服务器，正在重新连接。")
        await on_connect(bot=bot)


def on_mcrcon_connect(bot: Bot):
    try:
        mcr = MCRcon(get_mc_qq_ip(bot=bot), get_mc_qq_mcrcon_password(bot=bot), get_mc_qq_mcrcon_port(bot=bot))
        mcr.connect()
    except (OSError, ConnectionRefusedError):
        nonebot.logger.error("[MC_QQ_Rcon]丨无法连接到 MCRcon，正在重新连接。")
        time.sleep(3)
        on_mcrcon_connect(bot=bot)


def dis_mcrcon_connect():
    mcr.disconnect()


# 发送消息到 Minecraft
async def send_msg_to_mc(bot: Bot, event):
    text_msg, command_msg = await msg_process(bot=bot, event=event)
    try:
        mcr.command(command_msg)
    except (mcrcon.MCRconException, ConnectionResetError, ConnectionAbortedError):
        nonebot.logger.error("[MC_QQ_Rcon]丨无法发送消息，MCRcon 未连接。")
        on_mcrcon_connect(bot=bot)
        mcr.command(command_msg)
    nonebot.logger.success("[MC_QQ]丨发送消息：" + text_msg)
