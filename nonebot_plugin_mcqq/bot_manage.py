from nonebot import get_bots, get_driver, logger
from nonebot.adapters.minecraft import Bot as MinecraftBot
from nonebot.adapters.onebot.v11 import Bot as OneBotV11Bot
from nonebot.adapters.qq import Bot as QQBot

from .config import Server, plugin_config
from .data_source import (
    ONEBOT_GROUP_SERVER_DICT,
    QQ_GROUP_SERVER_DICT,
    QQ_GUILD_SERVER_DICT,
)

driver = get_driver()


@driver.on_bot_connect
async def on_bot_connected(bot: MinecraftBot):
    """当 Minecraft 服务器连接成功时"""
    server = plugin_config.server_dict.get(bot.self_id)
    if not server:
        logger.warning(
            f"[MC_QQ]丨未找到服务器 {bot.self_id} 的配置，将无法配置目标群聊"
        )
        return

    logger.info(f"[MC_QQ]丨服务器 {bot.self_id} 已成功连接。")

    # 建立映射
    for group in server.group_list:
        if group.adapter == "qq":
            QQ_GROUP_SERVER_DICT[group.group_id].append(bot.self_id)
        elif group.adapter == "onebot":
            ONEBOT_GROUP_SERVER_DICT[group.group_id].append(bot.self_id)

    for guild in server.guild_list:
        if guild.adapter == "qq":
            QQ_GUILD_SERVER_DICT[guild.channel_id].append(bot.self_id)
    if plugin_config.notice_connected:
        await notify_groups(server, bot.self_id, connected=True)


@driver.on_bot_disconnect
async def on_bot_disconnected(bot: MinecraftBot):
    """当 Minecraft 服务器断开连接时"""
    server: Server | None = plugin_config.server_dict.get(bot.self_id)
    if not server:
        return

    logger.info(f"[MC_QQ]丨服务器 {bot.self_id} 已断开连接。")

    def remove_mapping(target_dict: dict[str, list[str]], key: str):
        """安全移除"""
        if bot.self_id in target_dict[key]:
            target_dict[key].remove(bot.self_id)
            if not target_dict[key]:
                del target_dict[key]

    for group in server.group_list:
        if group.adapter == "qq":
            remove_mapping(QQ_GROUP_SERVER_DICT, group.group_id)
        elif group.adapter == "onebot":
            remove_mapping(ONEBOT_GROUP_SERVER_DICT, group.group_id)

    for guild in server.guild_list:
        if guild.adapter == "qq":
            remove_mapping(QQ_GUILD_SERVER_DICT, guild.channel_id)
    if plugin_config.notice_connected:
        await notify_groups(server, bot.self_id, connected=False)


async def notify_groups(server: Server, server_id: str, connected: bool):
    """
    向所有绑定的群聊或频道发送状态通知。
    :param server: 服务器配置
    :param server_id: 服务器ID
    :param connected: 连接状态
    """
    msg = (
        f"✅ 服务器 [{server_id}] 已成功连接！"
        if connected
        else f"⚠️ 服务器 [{server_id}] 已断开连接！"
    )

    for group in server.group_list:
        bot_id = group.bot_id
        adapter = group.adapter
        if not (bot := get_bots().get(bot_id)):
            logger.debug(
                f"[MC_QQ]丨未找到机器人 {bot_id}，跳过发送至群聊 {group.group_id} 的通知。"
            )
            continue
        try:
            if adapter == "qq" and isinstance(bot, QQBot):
                # TODO: 无需实现，QQ 群聊主动消息每个月就4条。等官方支持更多主动消息后再实现
                # await bot.send_to_c2c(openid=group.group_id, message=msg)
                logger.debug(
                    f"[MC_QQ]丨未实现的适配器: {group.adapter}，发送至群聊 {group.group_id}：一个月主动就四条，还是算了吧。"
                )
            elif adapter == "onebot" and isinstance(bot, OneBotV11Bot):
                await bot.call_api(
                    "send_group_msg", group_id=int(group.group_id), message=msg
                )
        except Exception as e:
            logger.warning(f"[MC_QQ]丨向群 {group.group_id} 发送通知失败: {e}")

    for guild in server.guild_list:
        bot_id = guild.bot_id
        adapter = guild.adapter
        try:
            bot = get_bots().get(bot_id)
            if adapter == "qq" and isinstance(bot, QQBot):
                await bot.send_to_channel(guild.channel_id, msg)
        except Exception as e:
            logger.warning(f"[MC_QQ]丨向频道 {guild.channel_id} 发送通知失败: {e}")
