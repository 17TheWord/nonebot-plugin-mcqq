from nonebot.plugin import PluginMetadata

from .config import Config

__plugin_meta__ = PluginMetadata(
    name="MC_QQ",
    description="基于NoneBot的与Minecraft Server互通消息的插件",
    homepage="https://github.com/17TheWord/nonebot-plugin-mcqq",
    usage="在群聊发送消息即可同步至 Minecraft 服务器",
    config=Config,
    type="application",
    supported_adapters={
        "nonebot.adapters.onebot.v11",
        "nonebot.adapters.minecraft",
        "nonebot.adapters.qq",
    },
)

from . import bot_manage as bot_manage
from . import on_minecraft_msg as on_minecraft_msg
from . import on_qq_msg as on_qq_msg
