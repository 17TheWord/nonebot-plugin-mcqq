from nonebot.adapters.minecraft import Message, MessageSegment
from nonebot.adapters.minecraft.models import (
    ClickAction,
    ClickEvent,
    Color,
    Component,
    HoverAction,
    HoverEvent,
)
from nonebot.adapters.onebot.v11 import Bot as OneBot
from nonebot.adapters.onebot.v11 import GroupMessageEvent as OneBotGroupMessageEvent
from nonebot.adapters.qq import Bot as QQBot
from nonebot.adapters.qq import GroupAtMessageCreateEvent as QQGroupAtMessageCreateEvent
from nonebot.adapters.qq import GuildMessageEvent as QQGuildMessageEvent

from ..config import plugin_config

# TODO 优化以下代码，添加过期机制

ONEBOT_GROUP_MEMBER_NICKNAME_CACHE = {}
"""缓存OneBot群成员昵称"""

ONEBOT_GROUP_NAME_CACHE = {}
"""缓存OneBot群名称"""

QQ_GUILD_MEMBER_NICKNAME_CACHE = {}
"""缓存QQ频道成员昵称"""

QQ_GUILD_NAME_CACHE = {}
"""缓存QQ频道名称"""

QQ_CHANNEL_NAME_CACHE = {}
"""缓存QQ子频道名称"""


async def __get_group_or_nick_name(
    bot: QQBot | OneBot,
    event: QQGuildMessageEvent | QQGroupAtMessageCreateEvent | OneBotGroupMessageEvent,
    user_id: str | None = None,
) -> str:
    """
    获取群名或者成员昵称，如果user_id为空则获取群名
    :param bot: 平台Bot实例
    :param event: 事件
    :param user_id: 用户ID
    :return: 昵称
    """
    if isinstance(event, OneBotGroupMessageEvent) and isinstance(bot, OneBot):
        if user_id:
            if event.user_id == int(user_id):
                return str(event.sender.card or event.sender.nickname)
            elif not (
                nickname := ONEBOT_GROUP_MEMBER_NICKNAME_CACHE.get(
                    (event.group_id, user_id)
                )
            ):
                nickname = (
                    await bot.get_group_member_info(
                        group_id=event.group_id, user_id=int(user_id), no_cache=True
                    )
                )["nickname"]
                ONEBOT_GROUP_MEMBER_NICKNAME_CACHE[(event.group_id, user_id)] = nickname
                return nickname
        elif not (group_name := ONEBOT_GROUP_NAME_CACHE.get(event.group_id)):
            group_name = (await bot.get_group_info(group_id=event.group_id))[
                "group_name"
            ]
            ONEBOT_GROUP_NAME_CACHE[event.group_id] = group_name
            return group_name

    elif isinstance(event, QQGuildMessageEvent) and isinstance(bot, QQBot):
        if user_id:
            if event.author.id == user_id:
                return str(
                    (event.member and event.member.nick) or event.author.username
                )
            elif not (
                member_name := QQ_GUILD_MEMBER_NICKNAME_CACHE.get(
                    (event.guild_id, user_id)
                )
            ):
                member = await bot.get_member(guild_id=event.guild_id, user_id=user_id)
                member_name = member.nick or (member.user and member.user.username)
                QQ_GUILD_MEMBER_NICKNAME_CACHE[(event.guild_id, user_id)] = member_name
                return str(member_name)
        else:
            if not (guild_name := QQ_GUILD_NAME_CACHE.get(event.guild_id)):
                guild = await bot.get_guild(guild_id=event.guild_id)
                guild_name = guild.name
                QQ_GUILD_NAME_CACHE[event.guild_id] = guild.name
            if not (channel_name := QQ_CHANNEL_NAME_CACHE.get(event.channel_id)):
                channel = await bot.get_channel(channel_id=event.channel_id)
                channel_name = channel.name
                QQ_CHANNEL_NAME_CACHE[event.channel_id] = channel.name

            return f"[{guild_name}/{channel_name}]"

    elif isinstance(event, QQGroupAtMessageCreateEvent) and isinstance(bot, QQBot):
        # TODO 等待QQ机器人完善API，目前主动消息条数太少，无法测试
        return event.author.member_openid if user_id else event.group_openid
    return "未知名称" if user_id else "[未知群名]"


def __normalize_url(url: str) -> str:
    """标准化URL，确保以http开头"""
    return url if url.startswith("http") else f"https://{url}"


def __create_hover_click_events(
    url: str, display_text: str
) -> tuple[HoverEvent, ClickEvent]:
    """
    创建带链接的HoverEvent和ClickEvent
    :param url: 链接地址
    :param display_text: 显示文本
    :return: HoverEvent和ClickEvent组件
    """
    hover_event = HoverEvent(
        action=HoverAction.show_text,
        contents=[Component(text=display_text, color=Color.dark_purple)],
    )
    click_event = ClickEvent(action=ClickAction.open_url, value=url)
    return hover_event, click_event


async def __get_common_qq_msg_parsing(
    bot: QQBot | OneBot,
    event: QQGuildMessageEvent | QQGroupAtMessageCreateEvent | OneBotGroupMessageEvent,
) -> tuple[Message, str]:
    """
    获取QQ消息解析后的消息列表和日志文本
    :param bot: Bot对象
    :param event: 事件对象
    :param rcon_mode: 是否为RCON模式
    :return: 消息列表和日志文本
    """
    log_text = ""
    message_list = Message()

    for msg in event.get_message():
        text = ""
        color = None
        hover_event = None
        click_event = None
        # 是否直接添加文本（不包装MessageSegment）
        raw_append = False

        # 处理文本消息
        if msg.type == "text":
            text = str(msg.data["text"]).replace("\r", "").replace("\n", "\n * ")
            raw_append = True

        # 处理图片/附件
        elif msg.type in ["image", "attachment"]:
            url = __normalize_url(msg.data["url"])
            ci_code = f"[[CICode,url={url}]]"

            if plugin_config.chat_image_enable:
                text = ci_code
                raw_append = True
            else:
                text = "[图片]"
                color = Color.light_purple
                hover_event = HoverEvent(
                    action=HoverAction.show_text,
                    contents=[Component(text=ci_code, color=Color.dark_purple)],
                )

        # 处理视频
        elif msg.type == "video":
            text = "[视频]"
            color = Color.light_purple
            url = __normalize_url(msg.data["url"])
            hover_event, click_event = __create_hover_click_events(url, text)

        # 处理分享
        elif msg.type == "share":
            text = "[分享]"
            color = Color.gold
            url = __normalize_url(msg.data["url"])
            hover_event, click_event = __create_hover_click_events(url, text)

        # 处理@消息（OneBot）
        elif msg.type == "at":
            if msg.data["qq"] == "all":
                text = "@全体成员"
            else:
                nickname = await __get_group_or_nick_name(bot, event, msg.data["qq"])
                text = f"@{nickname}"
            color = Color.green

        # 处理@用户（QQ）
        elif msg.type == "mention_user":
            nickname = await __get_group_or_nick_name(bot, event, msg.data["user_id"])
            text = f"@{nickname}"
            color = Color.green

        # 处理@子频道（QQ）
        elif msg.type == "mention_channel" and isinstance(event, QQGuildMessageEvent):
            if not (channel_name := QQ_CHANNEL_NAME_CACHE.get(event.channel_id)):
                channel = await bot.get_channel(channel_id=event.channel_id)
                channel_name = channel.name
                QQ_CHANNEL_NAME_CACHE[event.channel_id] = channel_name
            text = f"@{channel_name}"
            color = Color.green

        # 处理@全体成员（QQ）
        elif msg.type == "mention_everyone":
            text = "@全体成员"
            color = Color.green

        # 处理表情
        elif msg.type in ["face", "emoji"]:
            text = "[表情]"
            color = Color.green

        # 处理语音
        elif msg.type == "record":
            text = "[语音]"
            color = Color.gold

        # 未知类型
        else:
            text = "[未知消息类型]"

        # 统一处理文本和添加到消息列表
        display_text = text.strip() + " "
        log_text += display_text

        if raw_append:
            message_list.append(text + " ")
        else:
            message_list.append(
                MessageSegment.text(
                    text=display_text,
                    color=color,
                    hover_event=hover_event,
                    click_event=click_event,
                )
            )

    return message_list, log_text


async def parse_qq_msg_to_component(
    bot: QQBot | OneBot,
    event: QQGuildMessageEvent | QQGroupAtMessageCreateEvent | OneBotGroupMessageEvent,
    rcon_mode: bool = False,
) -> tuple[Message, str]:
    """
    解析 QQ 消息，转为 WebSocketBody 模型
    :param bot: 聊天平台Bot实例
    :param event: 所有事件
    :return: Message
    """

    message_list = Message()
    log_text = ""

    # 群聊名称
    if plugin_config.send_group_name:
        group_name = f"{await __get_group_or_nick_name(bot, event)} "
        message_list.append(MessageSegment.text(text=group_name, color=Color.aqua))
        log_text += group_name

    # 消息发送者昵称
    sender_nickname_text = await __get_group_or_nick_name(
        bot, event, str(event.get_user_id())
    )
    message_list.append(
        MessageSegment.text(text=sender_nickname_text, color=Color.green)
    )
    log_text += sender_nickname_text

    # 消息 '说：'
    message_list.append(
        MessageSegment.text(text=plugin_config.say_way, color=Color.white)
    )
    log_text += f" {plugin_config.say_way}"

    # 消息内容
    temp_message_list, msg_log_text = await __get_common_qq_msg_parsing(bot, event)
    log_text += msg_log_text

    message_list.append(*temp_message_list)

    return message_list, log_text


def parse_qq_screen_cmd_to_rcon_model(command_type: str, command: str):
    """
    解析 QQ 消息，转为 Rcon命令 模型
    :param command_type: 命令类型
    :param command: 命令内容
    :return: 命令文本
    """
    if command_type == "action_bar":
        return f'title @a actionbar "{command}"'
    else:
        return f'title @a "{command}"'
