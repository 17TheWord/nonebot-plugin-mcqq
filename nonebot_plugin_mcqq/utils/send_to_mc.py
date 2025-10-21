from collections.abc import Callable

from nonebot import get_bot, logger
from nonebot.adapters.minecraft import Bot
from nonebot.adapters.minecraft.exception import ActionFailed
from nonebot.adapters.onebot.v11 import Bot as OneBot
from nonebot.adapters.onebot.v11 import GroupMessageEvent as OneBotGroupMessageEvent
from nonebot.adapters.onebot.v11 import Message as OneBotMessage
from nonebot.adapters.qq import Bot as QQBot
from nonebot.adapters.qq import GroupAtMessageCreateEvent as QQGroupAtMessageCreateEvent
from nonebot.adapters.qq import GuildMessageEvent as QQGuildMessageEvent
from nonebot.adapters.qq import Message as QQMessage

from ..config import Server, plugin_config
from ..data_source import (
    ONEBOT_GROUP_SERVER_DICT,
    QQ_GROUP_SERVER_DICT,
    QQ_GUILD_SERVER_DICT,
)
from . import get_rcon_result, get_title
from .parse_qq_msg import parse_qq_msg_to_component


# 通用的服务器遍历逻辑
def get_mc_bot(server_name: str) -> Bot | None:
    """
    获取服务器 Bot
    :param server_name: 服务器名称
    :return: 服务器 Bot
    """
    try:
        return get_bot(server_name)  # type: ignore
    except (KeyError, ValueError):
        logger.warning(f"[MC_QQ]丨未找到服务器 {server_name} 的 Bot 或无可用 Bot")
    return None


def get_server_list(
    event: QQGroupAtMessageCreateEvent | QQGuildMessageEvent | OneBotGroupMessageEvent,
) -> list[str] | None:
    """
    根据事件获取绑定的服务器列表
    """
    if isinstance(event, QQGroupAtMessageCreateEvent):
        return QQ_GROUP_SERVER_DICT.get(event.group_openid)
    elif isinstance(event, QQGuildMessageEvent):
        return QQ_GUILD_SERVER_DICT.get(event.channel_id)
    elif isinstance(event, OneBotGroupMessageEvent):
        return ONEBOT_GROUP_SERVER_DICT.get(str(event.group_id))
    return None


async def for_each_server(
    event: QQGroupAtMessageCreateEvent | QQGuildMessageEvent | OneBotGroupMessageEvent,
    handler: Callable,
):
    """
    遍历服务器并执行处理逻辑
    :param event: 事件对象
    :param handler: 处理函数，接收 server_name 和 mc_bot
    """
    server_list = get_server_list(event) or []
    results = (
        OneBotMessage() if isinstance(event, OneBotGroupMessageEvent) else QQMessage()
    )
    # results.append("结果：")
    for server_name in server_list:
        if not (mc_bot := get_mc_bot(server_name)):
            results.append(f"服务器 {server_name} 未连接")
            continue
        if not (server := plugin_config.server_dict.get(server_name)):
            results.append(f"服务器 {server_name} 未配置")
            continue
        result = await handler(server_name, server, mc_bot)
        results.append(result)
    return results


# 具体的发送逻辑
async def send_actionbar_to_target_server(
    event: QQGroupAtMessageCreateEvent | QQGuildMessageEvent | OneBotGroupMessageEvent,
    action_bar: str,
):
    """
    发送actionbar到目标服务器
    """

    async def handler(server_name: str, server: Server, mc_bot: Bot):
        if server.rcon_msg:
            logger.info(f"[MC_QQ]丨通过 RCON 发送 ActionBar 到服务器 {server_name}")
            return await mc_bot.send_rcon_command(
                command=f"title @a actionbar ['{action_bar.strip()}']"
            )
        logger.info(
            f"[MC_QQ]丨通过 WebSocket API 发送 ActionBar 到服务器 {server_name}"
        )
        try:
            await mc_bot.send_actionbar(message=action_bar)
            return f"[{server_name}] 发送 ActionBar 成功"
        except ActionFailed as e:
            error_message = e.message if e.message else "未知错误"
            logger.error(
                f"[MC_QQ]丨发送 ActionBar 到服务器 {server_name} 失败，错误信息：{error_message}"
            )
            return f"[{server_name}]发送 ActionBar 失败：{error_message}"

    return await for_each_server(event, handler)


async def send_title_to_target_server(
    event: QQGroupAtMessageCreateEvent | QQGuildMessageEvent | OneBotGroupMessageEvent,
    title_message,
):
    """
    发送title到目标服务器
    """

    async def handler(server_name: str, server: Server, mc_bot: Bot):
        title, subtitle = get_title(title_message)
        if server.rcon_msg:
            title_result = await mc_bot.send_rcon_command(
                command=f'title @a title ["{title.strip()}"]'
            )
            subtitle_result = ""
            if subtitle:
                subtitle_result = await mc_bot.send_rcon_command(
                    command=f'title @a subtitle ["{subtitle.strip()}"]'
                )
            logger.info(f"[MC_QQ]丨通过 RCON 发送 Title 到服务器 {server_name}")
            return f"{title_result} {subtitle_result}"
        logger.info(f"[MC_QQ]丨通过 WebSocket API 发送 Title 到服务器 {server_name}")
        try:
            await mc_bot.send_title(title=title, subtitle=subtitle)
            return f"[{server_name}] 发送 Title 成功"
        except ActionFailed as e:
            error_message = e.message if e.message else "未知错误"
            logger.error(
                f"[MC_QQ]丨发送 Title 到服务器 {server_name} 失败，错误信息：{error_message}"
            )
            return f"[{server_name}]发送 Title 失败：{error_message}"

    return await for_each_server(event, handler)


async def send_message_to_target_server(
    bot: QQBot | OneBot,
    event: QQGroupAtMessageCreateEvent | QQGuildMessageEvent | OneBotGroupMessageEvent,
):
    """
    发送消息到目标服务器
    """

    async def handler(server_name: str, server: Server, mc_bot: Bot):
        message, log_text = await parse_qq_msg_to_component(bot=bot, event=event)
        if server.rcon_msg:
            await mc_bot.send_rcon_command(command=f'tellraw @a "[鹊桥] {log_text}"')
            logger.debug(
                f"[MC_QQ]丨通过 RCON 发送到服务器 [{server_name}] 的消息：{log_text}"
            )
        else:
            await mc_bot.send_msg(message=message)
            logger.debug(
                f"[MC_QQ]丨通过 WebSocket API 发送到服务器 [{server_name}] 的消息：{log_text}"
            )
        return f"已发送到服务器 {server_name}"

    return await for_each_server(event, handler)


async def send_command_to_target_server(
    event: QQGroupAtMessageCreateEvent | QQGuildMessageEvent | OneBotGroupMessageEvent,
    command: str,
):
    """
    发送命令到目标服务器
    """

    async def handler(server_name: str, server: Server, mc_bot: Bot):
        if not mc_bot:
            return f"服务器 {server_name} 未连接"
        result = await mc_bot.send_rcon_command(command=command)
        return get_rcon_result(result=f"[{server_name}] {result}", event=event)

    return await for_each_server(event, handler)
