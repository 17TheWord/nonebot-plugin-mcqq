from nonebot import get_driver
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot_plugin_guild_patch import GuildMessageEvent
from typing import Union

from mcqq_tool.config import Config

plugin_config: Config = Config.parse_obj(get_driver().config)

rule_guild_list = []
rule_group_list = []
for per_server in plugin_config.mc_qq_server_list:
    if guild_list := per_server.guild_list:
        for per_guild in guild_list:
            rule_guild_list.append(f"{per_guild.guild_id}:{per_guild.channel_id}")
    if group_list := per_server.group_list:
        for per_group in group_list:
            rule_group_list.append(per_group)


async def msg_rule(event: Union[GroupMessageEvent, GuildMessageEvent]) -> bool:
    """Rule 消息规则"""
    if isinstance(event, GroupMessageEvent):
        return event.group_id in rule_group_list
    elif isinstance(event, GuildMessageEvent):
        return f"{event.guild_id}:{event.channel_id}" in rule_guild_list
    return False
