from nonebot.adapters.minecraft import (
    Event as MinecraftEvent,
)
from nonebot.adapters.minecraft import (
    MessageEvent as MinecraftMessageEvent,
)
from nonebot.adapters.onebot.v11 import GROUP_ADMIN as ONEBOT_GROUP_ADMIN
from nonebot.adapters.onebot.v11 import GROUP_OWNER as ONEBOT_GROUP_OWNER
from nonebot.adapters.onebot.v11 import Bot as OneBot
from nonebot.adapters.onebot.v11 import GroupMessageEvent as OneBotGroupMessageEvent
from nonebot.adapters.qq import GUILD_ADMIN as QQ_GUILD_ADMIN
from nonebot.adapters.qq import GUILD_OWNER as QQ_GUILD_OWNER
from nonebot.adapters.qq import Bot as QQBot
from nonebot.adapters.qq import GroupAtMessageCreateEvent as QQGroupAtMessageCreateEvent
from nonebot.adapters.qq import GuildMessageEvent as QQGuildMessageEvent
from nonebot.adapters.qq.models.guild import GetGuildRolesReturn, Role
from nonebot.internal.matcher import Matcher
from nonebot.internal.permission import Permission
from nonebot.permission import SUPERUSER

from ..config import plugin_config
from ..data_source import (
    IGNORE_WORD_LIST,
    ONEBOT_GROUP_SERVER_DICT,
    QQ_GROUP_SERVER_DICT,
    QQ_GUILD_SERVER_DICT,
)


def mc_msg_rule(event: MinecraftEvent):
    if isinstance(event, MinecraftMessageEvent):
        if plugin_config.ignore_word_list:
            return not any(
                word in str(event.get_message()) for word in IGNORE_WORD_LIST
            )
    return event.server_name in plugin_config.server_dict.keys()


def all_msg_rule(
    event: QQGroupAtMessageCreateEvent | OneBotGroupMessageEvent | QQGuildMessageEvent,
):
    """
    检测是否为 绑定的群聊/频道
    :param event: QQGroupAtMessageCreateEvent | OneBotGroupMessageEvent | QQGuildMessageEvent
    :return: bool
    """
    if isinstance(event, QQGroupAtMessageCreateEvent):
        return event.group_openid in QQ_GROUP_SERVER_DICT.keys()
    elif isinstance(event, QQGuildMessageEvent):
        return event.channel_id in QQ_GUILD_SERVER_DICT.keys()
    elif isinstance(event, OneBotGroupMessageEvent):
        return str(event.group_id) in ONEBOT_GROUP_SERVER_DICT.keys()
    return False


# TODO 优化以下代码，添加过期机制

QQ_GUILD_ROLE_CACHE_DICT: dict[str, list[Role]] = {}
"""QQ 适配器 频道身份组缓存"""


async def __qq_guild_role_admin(bot: QQBot, event: QQGuildMessageEvent):
    """
    检测是否为 QQ适配器 指定身份组管理员
    :param bot: Bot
    :param event: GuildMessageEvent
    :return: bool
    """
    if not event.member or not event.member.roles:
        return False

    if not (guild_roles := QQ_GUILD_ROLE_CACHE_DICT.get(event.guild_id)):
        guild_roles_data: GetGuildRolesReturn = await bot.get_guild_roles(
            guild_id=event.guild_id
        )
        guild_roles = guild_roles_data.roles
        QQ_GUILD_ROLE_CACHE_DICT[event.guild_id] = guild_roles

    tem_roles = [
        role.id for role in guild_roles if role.name in plugin_config.guild_admin_roles
    ]
    return bool(set(event.member.roles) & set(tem_roles))


QQ_GUILD_ROLE_ADMIN = Permission(__qq_guild_role_admin)
"""QQ 适配器 频道管理身份组"""


async def permission_check(
    matcher: Matcher,
    bot: OneBot | QQBot,
    event: OneBotGroupMessageEvent | QQGroupAtMessageCreateEvent | QQGuildMessageEvent,
):
    """
    权限检查
    :param matcher: Matcher
    :param bot: OneBot | QQBot
    :param event: OneBotGroupMessageEvent | QQGroupAtMessageCreateEvent | QQGuildMessageEvent
    :return: None
    """
    if (
        (
            isinstance(event, OneBotGroupMessageEvent)
            and isinstance(bot, OneBot)
            and not await (ONEBOT_GROUP_ADMIN | ONEBOT_GROUP_OWNER | SUPERUSER)(
                bot, event
            )
        )
        or (
            # isinstance(event, OneBotGuildMessageEvent)
            # and isinstance(bot, OneBot)
            # and not await (
            #     ONEBOT_GUILD_ADMIN
            #     | ONEBOT_GUILD_OWNER
            #     | ONEBOT_GUILD_ROLE_ADMIN
            #     | SUPERUSER
            # )(bot, event)
        )
        or (
            isinstance(event, QQGuildMessageEvent)
            and isinstance(bot, QQBot)
            and not await (
                QQ_GUILD_ADMIN | QQ_GUILD_OWNER | SUPERUSER | QQ_GUILD_ROLE_ADMIN
            )(bot, event)
        )
        or (
            isinstance(event, QQGroupAtMessageCreateEvent)
            and isinstance(bot, QQBot)
            and not await SUPERUSER(bot, event)
        )
    ):
        await matcher.finish("你没有权限使用此命令")
