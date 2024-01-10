from nonebot import get_driver, logger
from nonebot.adapters.minecraft import Bot as MinecraftBot

from mcqq_tool.config import plugin_config
from mcqq_tool.rule import (
    QQ_GROUP_ID_LIST,
    QQ_GUILD_ID_LIST,
    ONEBOT_GROUP_ID_LIST,
    ONEBOT_GUILD_ID_LIST,
)

driver = get_driver()


@driver.on_bot_connect
async def on_bot_connected(bot: MinecraftBot):
    if server := plugin_config.mc_qq_server_dict.get(bot.self_id):
        for group in server.group_list:
            if group.adapter == "qq":
                if qq_group := QQ_GROUP_ID_LIST.get(group.group_id):
                    qq_group.append(bot.self_id)
                else:
                    QQ_GROUP_ID_LIST[group.group_id] = [bot.self_id]

            if group.adapter == "onebot":
                if onebot_group := ONEBOT_GROUP_ID_LIST.get(group.group_id):
                    onebot_group.append(bot.self_id)
                else:
                    ONEBOT_GROUP_ID_LIST[group.group_id] = [bot.self_id]

        for guild in server.guild_list:
            if guild.adapter == "qq":
                if qq_guild := QQ_GUILD_ID_LIST.get(guild.channel_id):
                    qq_guild.append(bot.self_id)
                else:
                    QQ_GUILD_ID_LIST[guild.channel_id] = [bot.self_id]

            if guild.adapter == "onebot":
                if onebot_guild := ONEBOT_GUILD_ID_LIST.get(f"{guild.guild_id}:{guild.channel_id}"):
                    onebot_guild.append(bot.self_id)
                else:
                    ONEBOT_GUILD_ID_LIST[f"{guild.guild_id}:{guild.channel_id}"] = [bot.self_id]
    else:
        logger.warning(f"[MC_QQ]丨未找到服务器 {bot.self_id} 的配置，将无法配置目标群聊")


@driver.on_bot_disconnect
async def on_bot_disconnected(bot: MinecraftBot):
    if server := plugin_config.mc_qq_server_dict.get(bot.self_id):
        for group in server.group_list:
            if group.adapter == "qq":
                if qq_group := QQ_GROUP_ID_LIST.get(group.group_id):
                    qq_group.remove(bot.self_id)

            if group.adapter == "onebot":
                if onebot_group := ONEBOT_GROUP_ID_LIST.get(group.group_id):
                    onebot_group.remove(bot.self_id)

        for guild in server.guild_list:
            if guild.adapter == "qq":
                if qq_guild := QQ_GUILD_ID_LIST.get(guild.channel_id):
                    qq_guild.remove(bot.self_id)

            if guild.adapter == "onebot":
                if onebot_guild := ONEBOT_GUILD_ID_LIST.get(f"{guild.guild_id}:{guild.channel_id}"):
                    onebot_guild.remove(bot.self_id)
