from nonebot import on_message
from nonebot.adapters.onebot.v11 import Bot, MessageEvent
from nonebot import get_driver

from .data_source import send_msg_to_mc, on_connect
from .utils import msg_rule

mc_qq = on_message(priority=5, rule=msg_rule, block=False)
driver = get_driver()


# bot连接时
@driver.on_bot_connect
async def on_start(bot: Bot):
    # 循环尝试连接
    while True:
        await on_connect(bot=bot)
        if not OSError:
            break


# 收到 群/频 道消息时
@mc_qq.handle()
async def handle_first_receive(bot: Bot, event: MessageEvent):
    await send_msg_to_mc(bot=bot, event=event)
