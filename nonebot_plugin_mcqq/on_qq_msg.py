from nonebot import on_command, on_message
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import Bot as OneBot
from nonebot.adapters.onebot.v11 import GroupMessageEvent as OneBotGroupMessageEvent
from nonebot.adapters.qq import Bot as QQBot
from nonebot.adapters.qq import GroupAtMessageCreateEvent as QQGroupAtMessageCreateEvent
from nonebot.adapters.qq import GuildMessageEvent as QQGuildMessageEvent
from nonebot.internal.matcher import Matcher
from nonebot.params import CommandArg

from .config import plugin_config
from .utils.rule import all_msg_rule, permission_check
from .utils.send_to_mc import (
    send_actionbar_to_target_server,
    send_command_to_target_server,
    send_message_to_target_server,
    send_title_to_target_server,
)

on_qq_msg = on_message(priority=plugin_config.command_priority + 1, rule=all_msg_rule)

on_qq_cmd = on_command(
    "minecraft_command",
    rule=all_msg_rule,
    aliases=plugin_config.command_header,
    priority=plugin_config.command_priority,
    block=plugin_config.command_block,
)

on_qq_send_title_cmd = on_command(
    "mcst",
    rule=all_msg_rule,
    priority=plugin_config.command_priority,
    block=plugin_config.command_block,
)

on_qq_send_actionbar_cmd = on_command(
    "mcsa",
    rule=all_msg_rule,
    priority=plugin_config.command_priority,
    block=plugin_config.command_block,
)


@on_qq_msg.handle()
async def handle_qq_msg(
    bot: QQBot | OneBot,
    event: QQGuildMessageEvent | QQGroupAtMessageCreateEvent | OneBotGroupMessageEvent,
):
    await send_message_to_target_server(bot=bot, event=event)


@on_qq_cmd.handle()
async def handle_qq_cmd(
    matcher: Matcher,
    bot: QQBot | OneBot,
    event: QQGuildMessageEvent | QQGroupAtMessageCreateEvent | OneBotGroupMessageEvent,
    args: Message = CommandArg(),
):
    if not (cmd := args.extract_plain_text()):
        await on_qq_cmd.finish("你没有输入命令")

    if cmd not in plugin_config.cmd_whitelist:
        await permission_check(matcher=matcher, bot=bot, event=event)

    temp_result = await send_command_to_target_server(event=event, command=cmd)
    await on_qq_cmd.finish(temp_result)


@on_qq_send_title_cmd.handle()
async def handle_qq_title_cmd(
    matcher: Matcher,
    bot: QQBot | OneBot,
    event: QQGuildMessageEvent | QQGroupAtMessageCreateEvent | OneBotGroupMessageEvent,
    args: Message = CommandArg(),
):
    await permission_check(matcher=matcher, bot=bot, event=event)

    if not (title := args.extract_plain_text()):
        await on_qq_send_title_cmd.finish("你没有输入任何标题")

    response = await send_title_to_target_server(event=event, title_message=title)
    await on_qq_send_title_cmd.finish(response)


@on_qq_send_actionbar_cmd.handle()
async def handle_qq_actionbar_cmd(
    matcher: Matcher,
    bot: QQBot | OneBot,
    event: QQGuildMessageEvent | QQGroupAtMessageCreateEvent | OneBotGroupMessageEvent,
    args: Message = CommandArg(),
):
    await permission_check(matcher=matcher, bot=bot, event=event)

    if not (action_bar := args.extract_plain_text()):
        await on_qq_send_actionbar_cmd.finish("你没有输入任何ActionBar信息")

    response = await send_actionbar_to_target_server(event=event, action_bar=action_bar)
    await on_qq_send_actionbar_cmd.finish(response)
