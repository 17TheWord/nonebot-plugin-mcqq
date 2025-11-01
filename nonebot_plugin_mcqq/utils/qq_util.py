from nonebot.adapters.onebot.v11 import Bot as OneBot
from nonebot.adapters.onebot.v11 import GroupMessageEvent as OneBotGroupMessageEvent
from nonebot.adapters.qq import Bot as QQBot
from nonebot.adapters.qq import GroupAtMessageCreateEvent as QQGroupAtMessageCreateEvent
from nonebot.adapters.qq import GuildMessageEvent as QQGuildMessageEvent
from nonebot.adapters.qq import MessageEvent as QQMessageEvent

# 缓存字典
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


async def get_qq_channel_name(bot: QQBot, channel_id: str) -> str:
    """
    获取子频道名称（带缓存）
    :param bot: QQ Bot实例
    :param channel_id: 子频道ID
    :return: 子频道名称
    """
    if not (channel_name := QQ_CHANNEL_NAME_CACHE.get(channel_id)):
        channel = await bot.get_channel(channel_id=channel_id)
        channel_name = channel.name
        QQ_CHANNEL_NAME_CACHE[channel_id] = channel_name
    return channel_name


async def get_group_or_nick_name(
    bot: QQBot | OneBot,
    event: QQMessageEvent | OneBotGroupMessageEvent,
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
        else:
            if not (group_name := ONEBOT_GROUP_NAME_CACHE.get(event.group_id)):
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
            channel_name = await get_qq_channel_name(bot, event.channel_id)
            return f"[{guild_name}/{channel_name}]"

    elif isinstance(event, QQGroupAtMessageCreateEvent) and isinstance(bot, QQBot):
        # TODO 等待QQ机器人完善API，目前主动消息条数太少，无法测试
        return event.author.member_openid if user_id else event.group_openid
    return "未知名称" if user_id else "[未知群名]"


def normalize_url(url: str) -> str:
    """标准化URL，确保以http开头"""
    return url if url.startswith("http") else f"https://{url}"
