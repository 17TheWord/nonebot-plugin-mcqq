import asyncio
from urllib.parse import quote_plus

import nonebot
from nonebot.adapters.minecraft import Adapter as MinecraftAdapter
from nonebug import App
import pytest


@pytest.mark.asyncio
async def test_on_bot_connected(app: App):
    """测试 Minecraft 服务器连接成功时的处理"""
    from nonebot_plugin_mcqq.data_source import (
        ONEBOT_GROUP_SERVER_DICT,
        QQ_GROUP_SERVER_DICT,
        QQ_GUILD_SERVER_DICT,
    )

    # 清空映射字典
    ONEBOT_GROUP_SERVER_DICT.clear()
    QQ_GROUP_SERVER_DICT.clear()
    QQ_GUILD_SERVER_DICT.clear()

    adapter = nonebot.get_adapter(MinecraftAdapter)
    # 模拟 bot 连接
    async with app.test_server() as ctx:
        client = ctx.get_client()
        headers = {
            "x-self-name": quote_plus("Server"),
            "Authorization": "Bearer test_access_token",
        }
        client.headers.update(headers)
        async with client.websocket_connect("/minecraft/ws", headers=headers) as ws:
            await asyncio.sleep(1)
            assert "Server" in nonebot.get_bots()
            assert "Server" in adapter.bots
            await ws.close()

        await asyncio.sleep(1)
        assert "Server" not in nonebot.get_bots()
        assert "Server" not in adapter.bots
