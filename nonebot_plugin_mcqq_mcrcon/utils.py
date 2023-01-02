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
        if event.message_type == "group":
            if event.group_id in per_server[1]:
                return True
        elif event.message_type == "guild":
            if [event.guild_id, event.channel_id] in per_server[2]:
                return True
    return False


async def send_msg_to_qq(bot: Bot, recv_msg):
    """发送消息到 QQ"""
    json_msg = json.loads(recv_msg)
    msg = json_msg['message']['data']
    if get_mc_qq_display_server_name():
        msg = f"[{json_msg['server_name']}] {json_msg['message']['data']}"
    # 循环服务器列表并发送消息
    if get_mc_qq_servers_list():
        for per_server in get_mc_qq_servers_list():
            if per_server[0] == json_msg['server_name']:
                if per_server[1]:
                    for per_group in per_server[1]:
                        logger.success(
                            f"[MC_QQ]丨[Server:{json_msg['server_name']}] to [Group:{per_group}] \"{msg}\"")
                        await bot.send_group_msg(
                            group_id=per_group,
                            message=msg
                        )
                if per_server[2]:
                    for per_guild in per_server[2]:
                        logger.success(
                            f"[MC_QQ]丨[Server:{json_msg['server_name']}] to [Guild:{per_guild[0]}/{per_guild[1]}] \"{msg}\"")
                        await bot.send_guild_channel_msg(
                            guild_id=per_guild[0],
                            channel_id=per_guild[1],
                            message=msg
                        )


async def get_member_nickname(bot: Bot, event: Union[GroupMessageEvent, GuildMessageEvent], user_id):
    """获取昵称"""
    # 判断从 群/频道 获取成员信息
    if event.message_type == "group":
        group_member_info = await bot.get_group_member_info(
            group_id=event.group_id,
            user_id=user_id,
            no_cache=True)
        if group_member_info['card'] == "":
            return group_member_info['nickname']
    else:
        # 返回频道成员昵称
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
        if event.message_type == "group":
            message_list.append(
                {"text": (await bot.get_group_info(group_id=event.group_id))['group_name'], "color": "aqua"})
        elif event.message_type == "guild":
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
            msg_dict = {"text": msg.data['text'].replace("\r\n", " "), "color": "white"}
            text_msg += msg.data['text'].replace("\r\n", " ")
        # 图片
        elif msg.type == "image":
            msg_dict = {"text": "[图片] ", "color": "yellow",
                        "clickEvent": {"action": "open_url", "value": msg.data['url']},
                        "hoverEvent": {"action": "show_text", "contents": [{"text": "查看图片", "color": "gold"}]}}
            text_msg += '[图片] '
        # 表情
        elif msg.type == "face":
            msg_dict = {"text": "[表情]", "color": "gold"}
            text_msg += '[表情] '
        # 语音
        elif msg.type == "record":
            msg_dict = {"text": "[语音]", "color": "light_purple"}
            text_msg += '[语音] '
        # 视频
        elif msg.type == "video":
            msg_dict = {"text": "[视频] ", "color": "light_purple",
                        "clickEvent": {"action": "open_url", "value": msg.data['url']},
                        "hoverEvent": {"action": "show_text", "contents": [{"text": "查看视频", "color": "dark_purple"}]}}
            text_msg += '[视频] '
        # @
        elif msg.type == "at":
            # 获取被@ 群/频道 昵称
            at_member_nickname = await get_member_nickname(bot, event, msg.data['qq'])
            msg_dict = {"text": "@" + at_member_nickname + " ", "color": "green"}
            text_msg += f"@{at_member_nickname} "
        # share
        elif msg.type == "share":
            msg_dict = {"text": "[分享：" + msg.data['title'] + "] ", "color": "yellow",
                        "clickEvent": {"action": "open_url", "value": msg.data['url']},
                        "hoverEvent": {"action": "show_text", "contents": [{"text": "查看图片", "color": "gold"}]}}
            text_msg += '[分享：' + msg.data['title'] + '] '
        # forward
        elif msg.type == "forward":
            # TODO 将合并转发消息拼接为字符串
            # 获取合并转发 await bot.get_forward_msg(message_id=event.message_id)
            msg_dict = {"text": "[合并转发] ", "color": "white"}
            text_msg += '[合并转发] '
        else:
            msg_dict = {"text": "[ " + msg.type + "] ", "color": "white"}
            text_msg += '[' + msg.type + '] '
        message_list.append(msg_dict)
    command_msg += json.dumps(message_list)
    return text_msg, command_msg


def get_mc_qq_group_list():
    """获取群列表"""
    try:
        return list(get_driver().config.mc_qq_group_list)
    except AttributeError:
        return []


def get_mc_qq_guild_list() -> list:
    """获取频道列表"""
    try:
        return list(get_driver().config.mc_qq_guild_list)
    except AttributeError:
        return []


def get_mc_qq_mcrcon_guild_admin_roles() -> list:
    """获取频道 MC_QQ 管理身份组"""
    try:
        return list(get_driver().config.mc_qq_mcrcon_guild_admin_roles)
    except AttributeError:
        return ["频道主", "管理员"]


def get_mc_qq_ip():
    """获取 IP"""
    try:
        return str(get_driver().config.mc_qq_ip)
    except AttributeError:
        return "127.0.0.1"


def get_mc_qq_ws_port():
    """获取 WebSocket 端口"""
    try:
        return int(get_driver().config.mc_qq_ws_port)
    except AttributeError:
        return 8765


def get_mc_qq_mcrcon_password():
    """获取 MCRcon 密码"""
    try:
        return str(get_driver().config.mc_qq_mcrcon_password)
    except AttributeError:
        return ""


def get_mc_qq_servers_list() -> list:
    """获取 服务器列表"""
    try:
        return list(get_driver().config.mc_qq_servers_list)
    except AttributeError:
        return []


def get_mc_qq_display_server_name() -> bool:
    """获取 是否显示服务器名称"""
    try:
        return bool(get_driver().config.MC_QQ_DISPLAY_SERVER_NAME)
    except AttributeError:
        return False


def get_mc_qq_send_group_name() -> bool:
    """获取 是否发送群聊名称"""
    try:
        return bool(get_driver().config.MC_QQ_SEND_GROUP_NAME)
    except AttributeError:
        return False


def get_mc_qq_mcrcon_rcon_list() -> dict:
    """获取 获取Rcon列表"""
    try:
        return dict(get_driver().config.mc_qq_mcrcon_rcon_list)
    except AttributeError:
        return {}
