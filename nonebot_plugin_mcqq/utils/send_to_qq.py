import re

from nonebot import get_bot, logger
from nonebot.adapters.onebot.v11 import Bot as OneBot
from nonebot.adapters.qq import AuditException
from nonebot.adapters.qq import Bot as QQBot

from ..config import plugin_config


async def send_mc_msg_to_qq(server_name: str, result: str):
    msg_result = re.sub(r"[&§].", "", result)
    if server := plugin_config.server_dict.get(server_name):
        if plugin_config.display_server_name:
            msg_result = f"[{server_name}] {msg_result}"

        for group in server.group_list:
            if bot := __get_target_bot(group.bot_id, True, group.group_id, msg_result):
                if group.adapter == "onebot" and isinstance(bot, OneBot):
                    try:
                        await bot.send_group_msg(
                            group_id=int(group.group_id), message=msg_result
                        )
                    except Exception as e:
                        logger.error(
                            f"[MC_QQ]丨发送至 OneBot Group {group.group_id} 的消息：{msg_result} 出现异常：{e!r}"
                        )
                elif group.adapter == "qq" and isinstance(bot, QQBot):
                    try:
                        await bot.post_group_messages(
                            group_openid=group.group_id, msg_type=0, content=msg_result
                        )
                    except AuditException as e:
                        logger.debug(
                            f"[MC_QQ]丨发送至 QQ Group {group.group_id} 的消息：{msg_result} 正在审核中"
                        )
                        try:
                            audit_result = await e.get_audit_result(3)
                            logger.debug(
                                f"[MC_QQ]丨审核结果：{audit_result.get_event_name()}"
                            )
                        except Exception as audit_error:
                            logger.error(
                                f"[MC_QQ]丨获取 QQ Group {group.group_id} 消息审核结果失败：{audit_error!r}"
                            )
                    except Exception as e:
                        logger.error(
                            f"[MC_QQ]丨发送至 QQ Group {group.group_id} 的消息：{msg_result} 出现异常：{e!r}"
                        )
                else:
                    logger.error(f"[MC_QQ]丨未知的适配器: {group.adapter}")

        for guild in server.guild_list:
            if bot := __get_target_bot(
                guild.bot_id, False, guild.channel_id, msg_result
            ):
                # if guild.adapter == "onebot":
                #     assert isinstance(bot, OneBot)
                #     await bot.send_guild_channel_msg(
                #         guild_id=guild.guild_id,
                #         channel_id=guild.channel_id,
                #         message=msg_result,
                #     )
                if guild.adapter == "qq" and isinstance(bot, QQBot):
                    try:
                        await bot.send_to_channel(
                            channel_id=guild.channel_id, message=msg_result
                        )
                    except AuditException as e:
                        logger.debug(
                            f"[MC_QQ]丨发送至 QQ Channel {guild.channel_id} 的消息：{msg_result} 正在审核中"
                        )
                        try:
                            audit_result = await e.get_audit_result(3)
                            logger.debug(
                                f"[MC_QQ]丨发送至 QQ Channel 消息的审核结果：{audit_result.get_event_name()}"
                            )
                        except Exception as audit_error:
                            logger.error(
                                f"[MC_QQ]丨获取 QQ Channel {guild.channel_id} 消息审核结果失败：{audit_error!r}"
                            )
                    except Exception as e:
                        logger.error(
                            f"[MC_QQ]丨发送至 QQ Channel {guild.channel_id} 的消息：{msg_result} 出现异常：{e!r}"
                        )
    else:
        logger.error(f"未知的服务器: {server_name}")


def __get_target_bot(
    bot_id: str, is_group: bool, target_group_id: str, message: str
) -> QQBot | OneBot | None:
    target_type = "群聊" if is_group else "子频道"
    try:
        return get_bot(bot_id)  # type: ignore
    except (KeyError, ValueError):
        logger.error(
            f'[MC_QQ]丨未找到bot: {bot_id}，发送至 [{target_type}@{target_group_id}] 失败: "{message}"'
        )
    return None
