from nonebot import get_driver, logger
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot_plugin_guild_patch import GuildMessageEvent

from typing import Union


async def msg_rule(event: Union[GroupMessageEvent, GuildMessageEvent]) -> bool:
    """Rule 消息规则"""
    for per_server in mc_qq_servers_list:
        if isinstance(event, GroupMessageEvent):
            if event.group_id in per_server['group_list']:
                return True
        elif isinstance(event, GuildMessageEvent):
            if {"guild_id": event.guild_id, "channel_id": event.channel_id} in per_server['guild_list']:
                return True
    return False


async def msg_to_qq_process(json_msg):
    """处理来自MC的消息，并返回处理后的消息"""
    message = {
        "PlayerJoinEvent": f"{json_msg['player']['nickname']} 加入了服务器",
        "PlayerQuitEvent": f"{json_msg['player']['nickname']} 离开了服务器",
        "AsyncPlayerChatEvent": f"{json_msg['player']['nickname']} 说：{json_msg['message']}",
        "PlayerDeathEvent": f"{json_msg['message']}",
    }
    return message[json_msg['event_name']]


async def send_msg_to_qq(bot: Bot, json_msg):
    """发送消息到 QQ"""
    msg = await msg_to_qq_process(json_msg)
    if mc_qq_display_server_name:
        msg = f"[{json_msg['server_name']}] {msg}"
    # 循环服务器列表并发送消息
    if mc_qq_servers_list:
        for per_server in mc_qq_servers_list:
            if per_server['server_name'] == json_msg['server_name']:
                if per_server['group_list']:
                    for per_group in per_server['group_list']:
                        logger.success(
                            f"[MC_QQ]丨from [{json_msg['server_name']}] to [群:{per_group}] \"{msg}\"")
                        await bot.send_group_msg(
                            group_id=per_group,
                            message=msg
                        )
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

    # 初始化消息
    text_msg = member_nickname + "说："
    # 初始化消息字典
    msgDict = {"senderName": member_nickname}

    # 发送群聊名称
    message_type = {}
    if get_mc_qq_send_group_name():
        if isinstance(event, GroupMessageEvent):
            message_type['type'] = "group"
            message_type['group_name'] = (await bot.get_group_info(group_id=event.group_id))['group_name']
        elif isinstance(event, GuildMessageEvent):
            message_type['type'] = "guild"
            message_type['guild_name'] = (await bot.get_guild_meta_by_guest(guild_id=event.guild_id))['guild_name']
            for per_channel in (await bot.get_guild_channel_list(guild_id=event.guild_id, no_cache=True)):
                if str(event.channel_id) == per_channel['channel_id']:
                    message_type['channel_name'] = per_channel['channel_name']
                    break
    else:
        message_type['type'] = "group"
        message_type['group_name'] = ""
    # 将消息类型以及群聊名称加入消息字典
    msgDict['message_type'] = message_type

    # 初始化消息列表
    messageList = []

    for msg in event.message:
        per_msg = {'msgType': msg.type}
        # 文本
        if msg.type == "text":
            msgData = msg.data['text'].replace("\r", "").replace("\n", "\n * ")
            text_msg += msgData
        # 图片
        elif msg.type == "image":
            msgData = msg.data['url']
            text_msg += '[图片]'
        # 表情
        elif msg.type == "face":
            msgData = '[表情]'
            text_msg += '[表情]'
        # 语音
        elif msg.type == "record":
            msgData = '[语音]'
            text_msg += '[语音]'
        # 视频
        elif msg.type == "video":
            msgData = msg.data['url']
            text_msg += '[视频]'
        # @
        elif msg.type == "at":
            # 获取被@ 群/频道 昵称
            at_member_nickname = await get_member_nickname(bot, event, msg.data['qq'])
            msgData = f"@{at_member_nickname}"
            text_msg += msgData
        # share
        elif msg.type == "share":
            msgData = msg.data['url']
            text_msg += '[分享：' + msg.data['title'] + ']'
        # forward
        elif msg.type == "forward":
            # TODO 将合并转发消息拼接为字符串
            # 获取合并转发 await bot.get_forward_msg(message_id=event.message_id)
            msgData = '[合并转发]'
            text_msg = msgData
        else:
            msgData = msg.type
            text_msg += '[' + msg.type + '] '

        text_msg += " "

        # 装入消息数据
        per_msg['msgData'] = msgData
        # 放入消息列表
        messageList.append(per_msg)

    # 消息列表添加至总消息
    msgDict['message'] = messageList
    return text_msg, str(msgDict)


def get_mc_qq_ws_ip() -> str:
    """获取 WebSocket IP"""
    try:
        return str(get_driver().config.mc_qq_ws_ip)
    except AttributeError:
        return "localhost"


def get_mc_qq_ws_port() -> int:
    """获取 WebSocket 端口"""
    try:
        return int(get_driver().config.mc_qq_ws_port)
    except AttributeError:
        return 8765


def get_mc_qq_send_group_name() -> bool:
    """获取 是否发送群聊名称"""
    try:
        return bool(get_driver().config.mc_qq_send_group_name)
    except AttributeError:
        return False


def get_mc_qq_display_server_name() -> bool:
    """获取 是否显示服务器名称"""
    try:
        return bool(get_driver().config.mc_qq_display_server_name)
    except AttributeError:
        return False


def get_mc_qq_servers_list() -> list:
    """获取 服务器列表"""
    try:
        return list(get_driver().config.mc_qq_servers_list)
    except AttributeError:
        return []


mc_qq_display_server_name = get_mc_qq_display_server_name()
mc_qq_servers_list = get_mc_qq_servers_list()
