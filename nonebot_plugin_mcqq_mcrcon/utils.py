from nonebot.adapters.onebot.v11 import Bot, MessageEvent


# Rule
async def msg_rule(bot: Bot, event: MessageEvent) -> bool:
    if event.message_type == "group":
        if event.group_id in get_mc_qq_group_list(bot):
            return True
    elif event.message_type == "guild":
        for per_channel in get_mc_qq_guild_list(bot=bot):
            if event.guild_id == per_channel[0] and event.channel_id == per_channel[1]:
                return True


# 发送消息到 QQ
async def send_msg_to_qq(bot, recv_msg):
    # 发送群消息
    if get_mc_qq_group_list(bot=bot):
        for per_group in get_mc_qq_group_list(bot=bot):
            await bot.call_api(
                "send_group_msg",
                group_id=per_group,
                message=recv_msg
            )
    # 发送频道消息
    if get_mc_qq_guild_list(bot=bot):
        for per_guild in get_mc_qq_guild_list(bot=bot):
            await bot.call_api(
                "send_guild_channel_msg",
                guild_id=per_guild[0],
                channel_id=per_guild[1],
                message=recv_msg
            )


# 获取昵称
async def get_member_nickname(bot: Bot, event, user_id):
    # 判断从 群 或者 频道 获取成员信息
    if event.message_type == "group":
        if event.sender.card == "":
            return event.sender.nickname
        else:
            member_info = await bot.call_api(
                "get_group_member_info",
                group_id=event.group_id,
                user_id=user_id,
                no_cache=True
            )
            return member_info['card']
        # 返回群成员群名片
    else:
        member_info = await bot.call_api(
            "get_guild_member_profile",
            guild_id=event.guild_id,
            user_id=user_id
        )
        # 返回频道成员昵称
        return member_info['nickname']


# 消息处理
async def msg_process(bot: Bot, event):
    # 获取昵称
    member_nickname = await get_member_nickname(bot, event, event.user_id)
    # 命令信息起始
    command_msg = 'tellraw @a ["",'
    # 插件名与发言人昵称
    command_msg += '{"text":"[MC_QQ] ","color":"yellow"},{"text":"' + \
                   (
                       member_nickname
                   ) + ' ","color":"aqua"},{"text":" 说：","color":"yellow"},'
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
                               'url'] + '"},"hoverEvent": {"action": "show_text","contents": [{"text": "查看图片","color": "gold"}]}},'
            text_msg += '[图片] '
        # 表情
        elif msg.type == "face":
            command_msg += '{"text": "[表情]","color": "gold"},'
            text_msg += '[表情] '
        # 语音
        elif msg.type == "record":
            command_msg += '{"text": "[语音]","color": "light_purple"},'
            text_msg += '[语音] '
        # 视频
        elif msg.type == "video":
            command_msg += '{"text": "[视频] ","color": "light_purple","clickEvent": {"action": "open_url","value": "' + \
                           msg.data[
                               'url'] + '"},"hoverEvent": {"action": "show_text","contents": [{"text": "查看视频","color": "dark_purple"}]}},'
            text_msg += '[视频] '
        # @
        elif msg.type == "at":
            # 获取被@ 群/频道 昵称
            at_member_nickname = await get_member_nickname(bot, event, msg.data['qq'])
            command_msg += '{"text": "@' + at_member_nickname + ' ","color": "green"},'
            text_msg += '@' + at_member_nickname + ' '
        # share
        elif msg.type == "share":
            command_msg += '{"text": "[分享：' + msg.data[
                'title'] + '] ","color": "yellow","clickEvent": {"action": "open_url","value": "' + msg.data[
                               'url'] + '"},"hoverEvent": {"action": "show_text","contents": [{"text": "查看图片","color": "gold"}]}},'
            text_msg += '[分享：' + msg.data['title'] + '] '
        # forward
        elif msg.type == "forward":
            # TODO 将合并转发消息拼接为字符串
            # 获取合并转发 await bot.get_forward_msg(message_id=event.message_id)
            command_msg += '{"text": "[合并转发] ","color": "white"},'
            text_msg += '[合并转发] '
        else:
            command_msg += '{"text": "[ ' + msg.type + '] ","color": "white"},'
            text_msg += '[' + msg.type + '] '
    command_msg += ']'
    command_msg = command_msg.replace("},]", "}]")
    return text_msg, command_msg


# 获取群列表
def get_mc_qq_group_list(bot: Bot):
    try:
        return list(bot.config.mc_qq_group_list)
    except AttributeError:
        return []


# 获取频道列表
def get_mc_qq_guild_list(bot: Bot) -> list:
    try:
        return list(bot.config.mc_qq_guild_list)
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
