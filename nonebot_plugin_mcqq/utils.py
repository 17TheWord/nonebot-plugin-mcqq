from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot_plugin_guild_patch import GuildMessageEvent


# 发送消息到 QQ
async def send_msg_to_qq(bot: Bot, recv_msg):
    # 发送群消息
    if get_mc_qq_group_list(bot=bot):
        for per_group in get_mc_qq_group_list(bot=bot):
            await bot.call_api("send_group_msg", group_id=per_group, message=recv_msg)
    # 发送频道消息
    if get_mc_qq_guild_list(bot=bot):
        for per_guild in get_mc_qq_guild_list(bot=bot):
            await bot.call_api("send_guild_channel_msg", guild_id=per_guild[0],
                               channel_id=per_guild[1], message=recv_msg)


# 获取昵称
async def get_member_nickname(bot: Bot, event, user_id):
    # 判断从 群 或者 频道 获取成员信息
    if isinstance(event, GroupMessageEvent):
        member_info = await bot.get_group_member_info(group_id=event.group_id, user_id=user_id)
    elif isinstance(event, GuildMessageEvent):
        await bot.get_guild_member_profile(guild_id=event.guild_id, user_id=str(user_id))
    # 返回成员昵称
    return member_info['nickname']


# 消息处理
async def msg_process(bot: Bot, event):
    # 初始化源消息
    msgJson = '{ "senderName": "' + event.sender.nickname + '", "message": ['
    text_msg = event.sender.nickname + '说：'
    for msg in event.message:
        msgJson += '{"msgType":"' + msg.type + '","msgData": "'
        # 文本
        if msg.type == "text":
            msgData = msg.data['text'].replace("\r\n", " ")
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
            # 获取 群/频道 昵称
            member_nickname = await get_member_nickname(bot, event, msg.data['qq'])
            msgData = '@' + member_nickname
        # share
        elif msg.type == "share":
            msgData = msg.data['url']
        # forward
        elif msg.type == "forward":
            msgData = '[合并转发]'
        else:
            msgData = '[' + msg.type + ']'
        text_msg += msgData
        msgJson += msgData + '"},'
    msgJson += ']}'
    return text_msg, msgJson


# 获取群列表
def get_mc_qq_group_list(bot: Bot):
    try:
        return list(bot.config.mc_qq_group_list)
    except AttributeError:
        return []


# 获取频道列表
def get_mc_qq_guild_list(bot: Bot):
    try:
        return bot.config.mc_qq_guild_list
    except AttributeError:
        return []


# 获取 IP
def get_mc_qq_ip(bot: Bot):
    try:
        return str(bot.config.mc_qq_ip)
    except AttributeError:
        return "127.0.0.1"


# 获取 WebSocket 端口
def get_mc_qq_ws_port(bot: Bot):
    try:
        return int(bot.config.mc_qq_ws_port)
    except AttributeError:
        return 8765


# 获取 MCRcon 端口
def get_mc_qq_mcrcon_port(bot: Bot):
    try:
        return int(bot.config.mc_qq_mcrcon_port)
    except AttributeError:
        return 25575


# 获取 MCRcon 密码
def get_mc_qq_mcrcon_password(bot: Bot):
    try:
        return str(bot.config.mc_qq_mcrcon_password)
    except AttributeError:
        return ""
