from typing import Union

from nonebot import on_message, on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.internal.matcher import Matcher
from nonebot.adapters.onebot.v11 import (
    Bot as OneBot,
    GroupMessageEvent as OneBotGroupMessageEvent,
)
from nonebot.adapters.qq import (
    Bot as QQBot,
    GuildMessageEvent as QQGuildMessageEvent,
    GroupAtMessageCreateEvent as QQGroupAtMessageCreateEvent,
)

from mcqq_tool.config import plugin_config
from mcqq_tool.rule import all_msg_rule, permission_check
from mcqq_tool.send_to_mc import (
    send_title_to_target_server,
    send_message_to_target_server,
    send_command_to_target_server,
    send_action_bar_to_target_server
)

on_qq_msg = on_message(priority=5, rule=all_msg_rule)

on_qq_cmd = on_command("minecraft_command", rule=all_msg_rule, aliases={"mcc"}, priority=4, block=True)

on_qq_send_title_cmd = on_command("send_title", rule=all_msg_rule, aliases={"mcst"}, priority=4, block=True)

on_qq_action_bar_cmd = on_command("action_bar", rule=all_msg_rule, aliases={"mca"}, priority=4, block=True)


@on_qq_msg.handle()
async def handle_qq_guild_msg(
        matcher: Matcher,
        bot: Union[
            QQBot,
            OneBot
        ],
        event: Union[
            QQGuildMessageEvent,
            QQGroupAtMessageCreateEvent,
            OneBotGroupMessageEvent,
            OneBotGroupMessageEvent
        ]
):
    await send_message_to_target_server(matcher=matcher, bot=bot, event=event)


@on_qq_cmd.handle()
async def handle_qq_group_cmd(
        matcher: Matcher,
        bot: Union[
            QQBot,
            OneBot
        ],
        event: Union[
            QQGuildMessageEvent,
            QQGroupAtMessageCreateEvent,
            OneBotGroupMessageEvent,
            OneBotGroupMessageEvent
        ],
        args: Message = CommandArg()
):
    if cmd := args.extract_plain_text():
        if cmd not in plugin_config.mc_qq_cmd_whitelist:
            await permission_check(matcher=matcher, bot=bot, event=event)

        temp_result = await send_command_to_target_server(matcher=matcher, bot=bot, event=event, command=cmd)

        await on_qq_cmd.finish(temp_result)
    else:
        await on_qq_cmd.finish("你没有输入命令")


@on_qq_send_title_cmd.handle()
async def handle_qq_send_title_cmd(
        matcher: Matcher,
        bot: Union[
            QQBot,
            OneBot
        ],
        event: Union[
            QQGuildMessageEvent,
            QQGroupAtMessageCreateEvent,
            OneBotGroupMessageEvent,
            OneBotGroupMessageEvent
        ],
        args: Message = CommandArg()
):
    await permission_check(matcher=matcher, bot=bot, event=event)
    if arg := args.extract_plain_text():
        response = await send_title_to_target_server(
            matcher=matcher,
            bot=bot,
            event=event,
            arg=arg,
        )
        await on_qq_send_title_cmd.finish(response)
    await on_qq_send_title_cmd.finish("你没有输入任何标题")


@on_qq_action_bar_cmd.handle()
async def handle_qq_send_title_cmd(
        matcher: Matcher,
        bot: Union[
            QQBot,
            OneBot
        ],
        event: Union[
            QQGuildMessageEvent,
            QQGroupAtMessageCreateEvent,
            OneBotGroupMessageEvent,
            OneBotGroupMessageEvent
        ],
        args: Message = CommandArg()
):
    await permission_check(matcher=matcher, bot=bot, event=event)
    if bar_msg := args.extract_plain_text():
        response = await send_action_bar_to_target_server(
            matcher=matcher,
            bot=bot,
            event=event,
            action_bar=bar_msg
        )
        await on_qq_action_bar_cmd.finish(response)
    await on_qq_action_bar_cmd.finish("你没有输入任何ActionBar信息")
