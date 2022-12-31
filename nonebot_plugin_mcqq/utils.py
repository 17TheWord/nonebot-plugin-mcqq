import json

from nonebot import get_driver, logger
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot_plugin_guild_patch import GuildMessageEvent


# Rule
async def msg_rule(event: GroupMessageEvent | GuildMessageEvent) -> bool:
    for per_server in get_mc_qq_servers_list():
        if event.message_type == "group":
            if event.group_id in per_server[1]:
                return True
        elif event.message_type == "guild":
            if [event.guild_id, event.channel_id] in per_server[2]:
                return True
    return False


# 发送消息到 QQ
async def send_msg_to_qq(bot: Bot, recv_msg):
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
                            f"[MC_QQ]丨from [{json_msg['server_name']}] to [群:{per_group}] \"{msg}\"")
                        await bot.send_group_msg(
                            group_id=per_group,
                            message=msg
                        )
                if per_server[2]:
                    for per_guild in per_server[2]:
                        logger.success(
                            f"[MC_QQ]丨from [{json_msg['server_name']}] to [频道:{per_guild[0]}/{per_guild[1]}] \"{msg}\"")
                        await bot.send_guild_channel_msg(
                            guild_id=per_guild[0],
                            channel_id=per_guild[1],
                            message=msg
                        )


# 获取昵称
async def get_member_nickname(bot: Bot, event, user_id):
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


# 消息处理
async def msg_process(bot: Bot, event: GroupMessageEvent | GuildMessageEvent):
    # 获取昵称
    member_nickname = await get_member_nickname(bot, event, event.user_id)

    # 初始化消息
    text_msg = member_nickname + "说："
    # 初始化消息字典
    msgDict = {"senderName": member_nickname}

    # 发送群聊名称
    message_type = {}
    if get_mc_qq_send_group_name():
        if event.message_type == "group":
            message_type['type'] = "group"
            message_type['group_name'] = (await bot.get_group_info(group_id=event.group_id))['group_name']
        elif event.message_type == "guild":
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
            msgData = msg.data['text'].replace("\r\n", " ").replace(" ", "") + " "
        # 图片
        elif msg.type == "image":
            msgData = msg.data['url']
        # 表情
        elif msg.type == "face":
            msgData = '[表情]'
        # 语音
        elif msg.type == "record":
            msgData = '[语音]'
        # 视频
        elif msg.type == "video":
            msgData = msg.data['url']
        # @
        elif msg.type == "at":
            # 获取被@ 群/频道 昵称
            msgData = '@' + (await get_member_nickname(bot, event, msg.data['qq']))
        # share
        elif msg.type == "share":
            msgData = msg.data['url']
        # forward
        elif msg.type == "forward":
            # TODO 将合并转发消息拼接为字符串
            # 获取合并转发 await bot.get_forward_msg(message_id=event.message_id)
            msgData = '[合并转发]'
        else:
            msgData = msg.type
        text_msg += msgData
        per_msg['msgData'] = msgData
        messageList.append(per_msg)
    msgDict['message'] = messageList
    print(msgDict)
    return text_msg, str(msgDict)


# 获取 IP
def get_mc_qq_ip() -> str:
    try:
        return str(get_driver().config.mc_qq_ip)
    except AttributeError:
        return "localhost"


# 获取 WebSocket 端口
def get_mc_qq_ws_port() -> int:
    try:
        return int(get_driver().config.mc_qq_ws_port)
    except AttributeError:
        return 8765


# 获取 MCRcon 端口
def get_mc_qq_mcrcon_port() -> int:
    try:
        return int(get_driver().config.mc_qq_mcrcon_port)
    except AttributeError:
        return 25575


# 获取 MCRcon 密码
def get_mc_qq_mcrcon_password() -> str:
    try:
        return str(get_driver().config.mc_qq_mcrcon_password)
    except AttributeError:
        return ""


# 获取 服务器列表
def get_mc_qq_servers_list() -> list:
    try:
        return list(get_driver().config.mc_qq_servers_list)
    except AttributeError:
        return []


# 获取 是否显示服务器名称
def get_mc_qq_display_server_name() -> bool:
    try:
        return bool(get_driver().config.mc_qq_display_server_name)
    except AttributeError:
        return False


# 获取 是否发送群聊名称
def get_mc_qq_send_group_name() -> bool:
    try:
        return bool(get_driver().config.mc_qq_send_group_name)
    except AttributeError:
        return False
