import re

from nonebot import logger
from nonebot.adapters.onebot.v11 import MessageEvent as OneBotMessageEvent
from nonebot.adapters.onebot.v11 import MessageSegment as OneBotMessageSegment
from nonebot.adapters.qq import MessageEvent as QQMessageEvent
from nonebot.adapters.qq import MessageSegment as QQMessageSegment

from ..config import plugin_config

if plugin_config.rcon_result_to_image:
    try:
        from .draw_result import draw_result_image
    except ImportError:
        logger.info("缺少 pillow 依赖，将关闭图片结果输出")
        plugin_config.rcon_result_to_image = False


def get_title(s: str) -> tuple[str, str]:
    newline_index = s.find("\n")
    if newline_index == -1:
        return s, ""
    else:
        part1 = s[:newline_index]
        part2 = s[newline_index + 1 :]
        return part1, part2


def get_rcon_result(result: str, event: QQMessageEvent | OneBotMessageEvent):
    if plugin_config.rcon_result_to_image:
        image = draw_result_image(result)
        if isinstance(event, QQMessageEvent):
            return QQMessageSegment.file_image(image)
        return OneBotMessageSegment.image(image)
    else:
        result = re.sub(r"[&§].", "", result)
        if isinstance(event, QQMessageEvent):
            return QQMessageSegment.text(result)
        return OneBotMessageSegment.text(result)
