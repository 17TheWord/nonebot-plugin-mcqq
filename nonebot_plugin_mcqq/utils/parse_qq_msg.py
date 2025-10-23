from nonebot.adapters.minecraft import Message as MCMessage
from nonebot.adapters.minecraft import MessageSegment
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
from nonebot.adapters.onebot.v11 import Message as OneBotMessage
from nonebot.adapters.qq import Bot as QQBot
from nonebot.adapters.qq import GroupAtMessageCreateEvent as QQGroupMessageEvent
from nonebot.adapters.qq import (
    GuildMessageEvent as QQGuildMessageEvent,
)
from nonebot.adapters.qq import (
    Message as QQMessage,
)

from ..config import plugin_config
from .qq_util import get_group_or_nick_name, get_qq_channel_name, normalize_url


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


async def __parse_message_to_mc_message_segment(
    message: QQMessage | OneBotMessage,
    bot: QQBot | OneBot,
    event,
    reply_mode: bool = False,
) -> tuple[list[Component], str]:
    log_text = ""

    component_list: list[Component] = []
    for msg in message:
        text = ""
        color: Color | None = None
        hover_event: HoverEvent | None = None
        click_event: ClickEvent | None = None
        ci_code = ""

        # 处理文本消息
        if msg.type == "text":
            text = str(msg.data["text"]).replace("\r", "").replace("\n", "\n * ")

        # 处理图片/附件
        elif msg.type in ["image", "attachment"]:
            text = "[图片]"
            url = normalize_url(msg.data["url"])
            ci_code = f"[[CICode,url={url}]]"

            color = Color.light_purple
            hover_event, click_event = __create_hover_click_events(url, "点击查看图片")

        # 处理视频
        elif msg.type == "video":
            text = "[视频]"
            color = Color.light_purple
            url = normalize_url(msg.data["url"])
            hover_event, click_event = __create_hover_click_events(url, "点击查看视频")

        # 处理分享
        elif msg.type == "share":
            text = "[分享]"
            color = Color.gold
            url = normalize_url(msg.data["url"])
            hover_event, click_event = __create_hover_click_events(url, "点击查看分享")

        # 处理@消息（OneBot）
        elif msg.type == "at":
            if msg.data["qq"] == "all":
                text = "@全体成员"
            else:
                text = f"@{await get_group_or_nick_name(bot, event, msg.data['qq'])}"
            color = Color.green

        # 处理@用户（QQ）
        elif msg.type == "mention_user":
            if reply_mode:
                text = "某用户"
            else:
                text = await get_group_or_nick_name(bot, event, msg.data["user_id"])
            color = Color.green

        # 处理@子频道（QQ）
        elif (
            msg.type == "mention_channel"
            and isinstance(event, QQGuildMessageEvent)
            and isinstance(bot, QQBot)
        ):
            channel_name = await get_qq_channel_name(bot, event.channel_id)
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
            text = f"[未知消息类型 {msg.type}]"

        # 统一处理文本和添加到消息列表
        log_text += text.strip() + " "
        if ci_code and plugin_config.chat_image_enable and not reply_mode:
            text = ci_code
        if reply_mode:
            component_list.append(Component(text=text, color=color))
        else:
            component_list.append(
                Component(
                    text=text,
                    color=color,
                    hoverEvent=hover_event,
                    clickEvent=click_event,
                )
            )

    return component_list, log_text


async def __process_reply_message(
    reply_message: OneBotMessage | QQMessage,
    reply_author_name: str,
    bot: OneBot | QQBot,
    event,
) -> tuple[MessageSegment, str]:
    """
    处理回复消息，生成 MessageSegment 和日志文本
    :param reply_message: 回复的消息内容
    :param reply_author_name: 回复消息作者的昵称
    :param bot: Bot实例
    :param event: 事件
    :return: MessageSegment 和日志文本
    """
    reply_mc_message, msg_log_text = await __parse_message_to_mc_message_segment(
        message=reply_message, bot=bot, event=event, reply_mode=True
    )
    reply_template = f" 回复 @{reply_author_name} 的消息 "

    message_segment = MessageSegment.text(
        text=reply_template,
        color=Color.gray,
        hover_event=HoverEvent(
            action=HoverAction.show_text,
            contents=reply_mc_message,
        ),
    )

    log_text = reply_template + msg_log_text
    return message_segment, log_text


async def parse_qq_msg_to_component(
    bot: QQBot | OneBot,
    event: QQGroupMessageEvent | QQGuildMessageEvent | OneBotGroupMessageEvent,
) -> tuple[MCMessage, str]:
    """
    解析 QQ 消息，转为 WebSocketBody 模型
    :param bot: 聊天平台Bot实例
    :param event: 所有事件
    :return: Message
    """

    message_list = MCMessage()
    log_text = ""

    # 群聊名称
    if plugin_config.send_group_name:
        group_name = f"{await get_group_or_nick_name(bot, event)} "
        message_list.append(MessageSegment.text(text=group_name, color=Color.aqua))
        log_text += group_name

    # 消息发送者昵称
    sender_nickname_text = await get_group_or_nick_name(
        bot, event, str(event.get_user_id())
    )
    message_list.append(
        MessageSegment.text(text=sender_nickname_text, color=Color.green)
    )
    log_text += sender_nickname_text

    # 回复消息（OneBot）
    if (
        isinstance(event, OneBotGroupMessageEvent)
        and isinstance(bot, OneBot)
        and (reply := event.reply)
    ):
        reply_author_name = str(
            reply.sender.card or reply.sender.nickname or "未知名称"
        )
        reply_segment, reply_log_text = await __process_reply_message(
            reply_message=reply.message,
            reply_author_name=reply_author_name,
            bot=bot,
            event=event,
        )
        message_list.append(reply_segment)
        log_text += reply_log_text
    # 回复消息（QQ）
    elif (
        isinstance(event, QQGuildMessageEvent)
        and isinstance(bot, QQBot)
        and (reply := event.reply)
    ):
        reply_author_name = str(reply.author.username or "未知名称")
        reply_segment, reply_log_text = await __process_reply_message(
            reply_message=QQMessage.from_guild_message(reply),
            reply_author_name=reply_author_name,
            bot=bot,
            event=event,
        )
        message_list.append(reply_segment)
        log_text += reply_log_text

    component_list, msg_log_text = await __parse_message_to_mc_message_segment(
        message=event.get_message(), bot=bot, event=event
    )

    # 消息 '说：'
    message_list.append(
        MessageSegment.text(
            text=plugin_config.say_way, color=Color.white, extra=component_list
        )
    )
    log_text += f" {plugin_config.say_way}"
    log_text += msg_log_text

    return message_list, log_text
