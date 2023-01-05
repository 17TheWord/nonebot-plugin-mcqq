import json
from typing import Union
from nonebot import get_driver, logger
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.internal.permission import Permission
from nonebot_plugin_guild_patch import GuildMessageEvent


async def _guild_admin(bot: Bot, event: GuildMessageEvent):
    """检测是否为频道管理员"""
    roles = set(
        role["role_name"]
        for role in (
            await bot.get_guild_member_profile(
                guild_id=event.guild_id, user_id=event.user_id
            )
        )["roles"]
    )
    return bool(roles & set(get_mc_qq_mcrcon_guild_admin_roles()))


GUILD_ADMIN: Permission = Permission(_guild_admin)
"""频道管理员权限"""


async def msg_rule(event: Union[GroupMessageEvent, GuildMessageEvent]) -> bool:
    """Rule 消息规则"""
    for per_server in get_mc_qq_servers_list():
        if isinstance(event, GroupMessageEvent):
            if event.group_id in per_server['group_list']:
                return True
        elif isinstance(event, GuildMessageEvent):
            if {"guild_id": event.guild_id, "channel_id": event.channel_id} in per_server['guild_list']:
                return True
    return False


async def send_msg_to_qq(bot: Bot, json_msg):
    """发送消息到 QQ"""
    msg = json_msg['message']['data']
    if get_mc_qq_display_server_name():
        msg = f"[{json_msg['server_name']}] {json_msg['message']['data']}"
    # 循环服务器列表并发送消息
    if get_mc_qq_servers_list():
        for per_server in get_mc_qq_servers_list():
            # 如果服务器名相同
            if per_server['server_name'] == json_msg['server_name']:
                # 如果群列表存在
                if per_server['group_list']:
                    for per_group in per_server['group_list']:
                        logger.success(
                            f"[MC_QQ]丨from [{json_msg['server_name']}] to [群:{per_group}] \"{msg}\"")
                        await bot.send_group_msg(
                            group_id=per_group,
                            message=msg
                        )
                # 如果频道列表存在
                if per_server['guild_list']:
                    for per_guild in per_server['guild_list']:
                        logger.success(
                            f"[MC_QQ]丨from [{json_msg['server_name']}] to [频道:{per_guild['guild_id']}/{per_guild['channel_id']}] \"{msg}\"")
                        await bot.send_guild_channel_msg(
                            guild_id=per_guild['guild_id'],
                            channel_id=per_guild['channel_id'],
                            message=msg
                        )


async def get_member_nickname(bot: Bot, event: Union[GroupMessageEvent, GuildMessageEvent], user_id):
    """获取昵称"""
    # 判断从 群/频道 获取成员信息
    if isinstance(event, GroupMessageEvent):
        # 如果获取发送者的昵称
        if event.user_id == int(user_id):
            # 如果群名片为空，则发送昵称
            if event.sender.card == "":
                return event.sender.nickname
            # 如果群名片不为空，发送群名片
            else:
                return event.sender.card
        # 如果获取其他人的昵称
        else:
            return (await bot.get_group_member_info(
                group_id=event.group_id,
                user_id=user_id,
                no_cache=True
            ))['nickname']
    elif isinstance(event, GuildMessageEvent):
        # 返回频道成员昵称
        if event.user_id == user_id:
            return event.sender.nickname
        else:
            return (await bot.get_guild_member_profile(
                guild_id=event.guild_id,
                user_id=user_id))['nickname']


async def msg_process(bot: Bot, event: Union[GroupMessageEvent, GuildMessageEvent]):
    """消息处理"""
    # 获取昵称
    member_nickname = await get_member_nickname(bot, event, event.user_id)

    # 初始化日志消息
    text_msg = member_nickname + " 说："

    command_msg = "tellraw @p "

    message_list = [
        {"text": "[MC_QQ] ", "color": "yellow"},
    ]
    if get_mc_qq_send_group_name():
        if isinstance(event, GroupMessageEvent):
            message_list.append(
                {"text": (await bot.get_group_info(group_id=event.group_id))['group_name'] + " ", "color": "aqua"})
        elif isinstance(event, GuildMessageEvent):
            guild_name = (await bot.get_guild_meta_by_guest(guild_id=event.guild_id))['guild_name']
            for per_channel in (await bot.get_guild_channel_list(guild_id=event.guild_id, no_cache=True)):
                if str(event.channel_id) == per_channel['channel_id']:
                    message_list.append({"text": guild_name + "丨" + per_channel['channel_name'] + " ", "color": "aqua"})
                    break
    message_list.append({"text": member_nickname, "color": "aqua"})
    message_list.append({"text": " 说：", "color": "yellow"})

    for msg in event.message:
        # 文本
        if msg.type == "text":
            msg_dict = {"text": msg.data['text'].replace("\r", "").replace("\n", "\n * ") + " ", "color": "white"}
            text_msg += msg.data['text'].replace("\r", "").replace("\n", "\n * ")
        # 图片
        elif msg.type == "image":
            msg_dict = {"text": "[图片] ", "color": "yellow",
                        "clickEvent": {"action": "open_url", "value": msg.data['url']},
                        "hoverEvent": {"action": "show_text", "contents": [{"text": "查看图片", "color": "gold"}]}
                        }
            text_msg += '[图片]'
        # 表情
        elif msg.type == "face":
            msg_dict = {"text": "[表情] ", "color": "gold"}
            text_msg += '[表情]'
        # 语音
        elif msg.type == "record":
            msg_dict = {"text": "[语音] ", "color": "light_purple"}
            text_msg += '[语音]'
        # 视频
        elif msg.type == "video":
            msg_dict = {"text": "[视频] ", "color": "light_purple",
                        "clickEvent": {"action": "open_url", "value": msg.data['url']},
                        "hoverEvent": {"action": "show_text", "contents": [{"text": "查看视频", "color": "dark_purple"}]}
                        }
            text_msg += '[视频]'
        # @
        elif msg.type == "at":
            # 获取被@ 群/频道 昵称
            at_member_nickname = await get_member_nickname(bot, event, msg.data['qq'])
            msg_dict = {"text": "@" + at_member_nickname + " ", "color": "green"}
            text_msg += f"@{at_member_nickname}"
        # share
        elif msg.type == "share":
            msg_dict = {"text": "[分享：" + msg.data['title'] + "] ", "color": "yellow",
                        "clickEvent": {"action": "open_url", "value": msg.data['url']},
                        "hoverEvent": {"action": "show_text", "contents": [{"text": "查看图片", "color": "gold"}]}
                        }
            text_msg += '[分享：' + msg.data['title'] + ']'
        # forward
        elif msg.type == "forward":
            # TODO 将合并转发消息拼接为字符串
            # 获取合并转发 await bot.get_forward_msg(message_id=event.message_id)
            msg_dict = {"text": "[合并转发] ", "color": "white"}
            text_msg += '[合并转发]'
        else:
            msg_dict = {"text": "[ " + msg.type + "] ", "color": "white"}
            text_msg += '[' + msg.type + ']'

        # 放入消息列表
        message_list.append(msg_dict)

    # 拼接完整命令
    command_msg += json.dumps(message_list)
    return text_msg, command_msg


def get_mc_qq_ws_ip():
    """获取 WebSocket IP"""
    try:
        return str(get_driver().config.mc_qq_ws_ip)
    except AttributeError:
        return "127.0.0.1"


def get_mc_qq_ws_port():
    """获取 WebSocket 端口"""
    try:
        return int(get_driver().config.mc_qq_ws_port)
    except AttributeError:
        return 8765


def get_mc_qq_send_group_name() -> bool:
    """获取 是否发送群聊名称"""
    try:
        return bool(get_driver().config.MC_QQ_SEND_GROUP_NAME)
    except AttributeError:
        return False


def get_mc_qq_display_server_name() -> bool:
    """获取 是否显示服务器名称"""
    try:
        return bool(get_driver().config.MC_QQ_DISPLAY_SERVER_NAME)
    except AttributeError:
        return False


def get_mc_qq_servers_list() -> list:
    """获取 服务器列表"""
    try:
        return list(get_driver().config.mc_qq_servers_list)
    except AttributeError:
        return []


def get_mc_qq_mcrcon_password():
    """获取 MCRcon 密码"""
    try:
        return str(get_driver().config.mc_qq_mcrcon_password)
    except AttributeError:
        return ""


def get_mc_qq_mcrcon_rcon_list() -> dict:
    """获取 获取Rcon列表"""
    try:
        return dict(get_driver().config.mc_qq_mcrcon_rcon_list)
    except AttributeError:
        return {}


def get_mc_qq_mcrcon_guild_admin_roles() -> list:
    """获取频道 MC_QQ 管理身份组"""
    try:
        return list(get_driver().config.mc_qq_mcrcon_guild_admin_roles)
    except AttributeError:
        return ["频道主", "管理员"]
