import mcrcon
import websockets
import nonebot
from mcrcon import MCRcon

from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot_plugin_guild_patch import GuildMessageEvent

from src.mc_qq_config import group_list, mc_ip, ws_port, mcrcon_password, mcrcon_port

# 配置 MCRcon 连接信息
# TODO 从 .env.* 配置文件获取连接信息
mcr = MCRcon(mc_ip, mcrcon_password, mcrcon_port)


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
                get_msg = await websocket.recv()

                if group_list['group_list']:
                    for per_group in group_list['group_list']:
                        await bot.call_api("send_group_msg", group_id=per_group, message=get_msg)
                if group_list['guild_list']:
                    for per_guild in group_list['guild_list']:
                        await bot.call_api("send_guild_channel_msg", guild_id=per_guild['guild_id'],
                                           channel_id=per_guild['channel_id'], message=get_msg)
                nonebot.logger.success("[MC_QQ]丨发送消息：" + get_msg)
    except (OSError, websockets.exceptions.ConnectionClosedError, websockets.exceptions.ConnectionClosedOK):
        nonebot.logger.error("[MC_QQ]丨无法连接到 MC_QQ WebSocket 服务器，正在重新连接。")
        await on_connect(bot=bot)


async def on_mcrcon_connect():
    try:
        mcr.connect()
    except (OSError, ConnectionRefusedError):
        nonebot.logger.error("[MC_QQ_Rcon]丨无法连接到 MCRcon，正在重新连接。")
        await on_mcrcon_connect()


# 发送消息到 Minecraft
async def send_msg_to_mc(bot, event):
    # 命令信息起始
    command_msg = 'tellraw @a ["",'
    # 插件名与发言人昵称
    command_msg += '{"text": "[MC_QQ] ' + event.sender.nickname + '说：","color": "white"},'
    # 文本信息
    text_msg = ''
    for msg in event.message:
        # 文本
        if msg.type == "text":
            command_msg += '{"text": "' + msg.data['text'].replace("\r\n", " ") + ' ","color": "white"},'
            text_msg += msg.data['text'].replace("\r\n", " ")
        # 图片
        elif msg.type == "image":
            command_msg += '{"text": "[图片] ","color": "yellow","clickEvent": {"action": "open_url","value": "' + \
                           msg.data[
                               'url'] + '"},"hoverEvent": {"action": "show_text","contents": [{"text": "查看图片","color": "dark_purple"}]}},'
            text_msg += '[图片] '
        # 表情
        elif msg.type == "face":
            command_msg += '{"text": "[表情]","color": "white"},'
            text_msg += '[表情] '
        # 语音
        elif msg.type == "record":
            command_msg += '{"text": "[语音]","color": "white"},'
            text_msg += '[语音] '
        # 视频
        elif msg.type == "video":
            command_msg += '{"text": "[视频] ","color": "yellow","clickEvent": {"action": "open_url","value": "' + \
                           msg.data[
                               'url'] + '"},"hoverEvent": {"action": "show_text","contents": [{"text": "查看视频","color": "dark_purple"}]}},'
            text_msg += '[视频] '
        # @
        elif msg.type == "at":
            # 获取 群/频道 昵称
            member_nickname = await get_member_nickname(bot, event, msg.data['qq'])
            command_msg += '{"text": "@' + member_nickname + ' ","color": "aqua"},'
            text_msg += '@' + member_nickname + ' '
        # share
        elif msg.type == "share":
            command_msg += '{"text": "[分享：' + msg.data[
                'title'] + '] ","color": "yellow","clickEvent": {"action": "open_url","value": "' + msg.data[
                               'url'] + '"},"hoverEvent": {"action": "show_text","contents": [{"text": "查看图片","color": "dark_purple"}]}},'
            text_msg += '[分享：' + msg.data['title'] + '] '
        # forward
        elif msg.type == "forward":
            # 获取合并转发 await bot.get_forward_msg(message_id=event.message_id)
            command_msg += '{"text": "[合并转发] ","color": "white"},'
            text_msg += '[合并转发] '
        else:
            command_msg += '{"text": "[ ' + msg.type + '] ","color": "white"},'
            text_msg += '[' + msg.type + '] '
    command_msg += ']'
    command_msg = command_msg.replace("},]", "}]")
    try:
        mcr.command(command_msg)
    except (mcrcon.MCRconException, ConnectionResetError):
        nonebot.logger.error("[MC_QQ_Rcon]丨无法发送消息，MCRcon 未连接。")
    except ConnectionAbortedError:
        await on_mcrcon_connect()
        mcr.command(command_msg)
    nonebot.logger.success("[MC_QQ]丨发送消息：" + text_msg)


# 获取昵称
async def get_member_nickname(bot, event, user_id):
    # 判断从 群 或者 频道 获取成员信息
    if isinstance(event, GroupMessageEvent):
        member_info = await bot.get_group_member_info(group_id=event.group_id, user_id=user_id)
    elif isinstance(event, GuildMessageEvent):
        await bot.get_guild_member_profile(guild_id=event.guild_id, user_id=str(user_id))
    # 返回成员昵称
    return member_info['nickname']
