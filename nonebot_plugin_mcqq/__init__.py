from typing import Union

from mcqq_tool.config import Config
from mcqq_tool.permission import permission_check
from mcqq_tool.utils import send_msg_to_mc, send_cmd_to_mc, send_send_title_to_mc
from nonebot import on_message, on_command, get_driver
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import Bot as OneBot, GroupMessageEvent
from nonebot.adapters.qq import Bot as QQBot, MessageCreateEvent
from nonebot.drivers import ASGIMixin
from nonebot.internal.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot_plugin_guild_patch import GuildMessageEvent

from .data_source import set_route
from .utils import msg_rule

__plugin_meta__ = PluginMetadata(
    name="MC_QQ",
    description="基于NoneBot的与Minecraft Server互通消息的插件",
    homepage="https://github.com/17TheWord/nonebot-plugin-mcqq",
    usage="在群聊发送消息即可同步至 Minecraft 服务器",
    config=Config,
    type="application",
    supported_adapters={
        "nonebot.adapters.onebot.v11"
        "nonebot.adapters.qq"
    }
)

mc_qq = on_message(priority=2, rule=msg_rule)

mc_qq_send_title = on_command(
    "mc_qq_send_title",
    aliases={"mcst"},
    priority=1,
    rule=msg_rule,
    block=True
)

mc_qq_cmd = on_command(
    "minecraft_command",
    aliases={"mcc"},
    priority=1,
    rule=msg_rule,
    block=True
)

driver = get_driver()


# bot连接时
@driver.on_startup
async def on_start():
    # 启动 WebSocket 服务器
    if isinstance(driver, ASGIMixin):
        await set_route(driver=driver)


# 收到消息时
@mc_qq.handle()
async def handle_msg(
        bot: Union[OneBot, QQBot],
        event: Union[GroupMessageEvent, GuildMessageEvent, MessageCreateEvent]
):
    if result := await send_msg_to_mc(bot=bot, event=event):
        await mc_qq.finish(result)


# 收到命令时
@mc_qq_cmd.handle()
async def handle_cmd(
        matcher: Matcher,
        bot: Union[OneBot, QQBot],
        event: Union[GroupMessageEvent, GuildMessageEvent, MessageCreateEvent],
        args: Message = CommandArg()
):
    await permission_check(matcher=matcher, bot=bot, event=event)
    if back_msg := await send_cmd_to_mc(event=event, cmd=args.extract_plain_text()):
        await mc_qq_cmd.finish(back_msg)


@mc_qq_send_title.handle()
async def handle_title(
        matcher: Matcher,
        bot: Union[OneBot, QQBot],
        event: Union[GroupMessageEvent, GuildMessageEvent, MessageCreateEvent],
        args: Message = CommandArg()
):
    await permission_check(matcher=matcher, bot=bot, event=event)
    if arg := args.extract_plain_text():
        if back_msg := await send_send_title_to_mc(event=event, arg=arg):
            await mc_qq_send_title.finish(back_msg)
