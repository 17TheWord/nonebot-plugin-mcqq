from nonebot import on_command, on_message
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import Bot as OneBot
from nonebot.adapters.onebot.v11 import GroupMessageEvent as OneBotGroupMessageEvent
from nonebot.adapters.qq import Bot as QQBot
from nonebot.adapters.qq import GroupAtMessageCreateEvent as QQGroupAtMessageCreateEvent
from nonebot.adapters.qq import GuildMessageEvent as QQGuildMessageEvent
from nonebot.internal.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.rule import to_me

from .config import plugin_config
from .utils.rule import all_msg_rule, permission_check
from .utils.send_to_mc import (
    send_actionbar_to_target_server,
    send_command_to_target_server,
    send_message_to_target_server,
    send_title_to_target_server,
)
from .utils.link_data_manager import LinkDataManager

import datetime

link_data_manager = LinkDataManager("user_qq_links.json")

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

on_qq_link = on_command("link", rule=to_me(), aliases={"连接", "绑定","bind","注册"}, priority=10, block=True)


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

    
@on_qq_link.handle()
async def handle_qq_link(
    matcher: Matcher,
    bot: QQBot | OneBot,
    event: QQGuildMessageEvent | QQGroupAtMessageCreateEvent | OneBotGroupMessageEvent,
    args: Message = CommandArg(),
):
    if(plugin_config.auto_whitelist==True):
        if isinstance(event, OneBotGroupMessageEvent):
            if usr_id := args.extract_plain_text():
                await on_qq_link.send(f"尝试绑定正版玩家账号[{usr_id}]到当前QQ账号")
                timestamp = event.time
                local_time = datetime.datetime.fromtimestamp(timestamp)
                time_str = local_time.strftime("%Y-%m-%d %H:%M:%S")
                qq_id_str = str(event.user_id)
                if link_data_manager.add_entry(usr_id,qq_id_str,time_str,1)!=True:
                    await on_qq_link.finish("当前QQ或游戏账号已被绑定!")
                else:
                    # await on_qq_link.send(f"/whitelist add {qq_id_str}")
                    temp_result = await send_command_to_target_server(event=event, command=f"/whitelist add {usr_id}")
                    await on_qq_link.finish(f"玩家账号[{usr_id}]成功绑定到当前QQ：{qq_id_str}")
                    # await on_qq_link.finish(temp_result)

            else:
                await on_qq_link.finish("请按照格式[link/绑定 usr_id]进行账号绑定!")

        
