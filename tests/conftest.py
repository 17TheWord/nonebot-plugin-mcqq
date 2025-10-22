import os

import nonebot
from nonebot.adapters.minecraft import Adapter as MinecraftAdapter
from nonebot.adapters.onebot.v11 import Adapter as OneBotV11Adapter
from nonebot.adapters.qq import Adapter as QQAdapter
from nonebug import NONEBOT_INIT_KWARGS
import pytest
from pytest_asyncio import is_async_test


def pytest_collection_modifyitems(items: list[pytest.Item]):
    pytest_asyncio_tests = (item for item in items if is_async_test(item))
    session_scope_marker = pytest.mark.asyncio(loop_scope="session")
    for async_test in pytest_asyncio_tests:
        async_test.add_marker(session_scope_marker, append=False)


@pytest.fixture(scope="session", autouse=True)
async def after_nonebot_init(after_nonebot_init: None):
    # 加载适配器
    driver = nonebot.get_driver()
    driver.register_adapter(MinecraftAdapter)
    driver.register_adapter(OneBotV11Adapter)
    driver.register_adapter(QQAdapter)

    # 加载插件
    nonebot.load_from_toml("pyproject.toml")


os.environ["ENVIRONMENT"] = "test"


def pytest_configure(config: pytest.Config):
    """配置 NoneBot 初始化参数

    驱动器：FastAPI + WebSockets + HTTPX
    适配器配置：Minecraft 访问令牌

    测试服务器名：test_server

    映射群聊：
    - 适配器：OneBot，机器人 ID：int(123456789)，群号：int(1234567890)
    - 适配器：QQ，机器人 ID："987654321"，群号："654321"

    映射频道：
    - 适配器：QQ，机器人 ID："987654321"，子频道号："9876543210"
    """
    config.stash[NONEBOT_INIT_KWARGS] = {
        "driver": "~fastapi+~websockets+~httpx",
        "superusers": {"999999999"},
        "minecraft_access_token": "test_access_token",
        "mc_qq": {
            "server_dict": {
                "test_server": {
                    "group_list": [
                        {
                            "adapter": "onebot",
                            "bot_id": "123456789",
                            "group_id": "1234567890",
                        },
                        {"adapter": "qq", "bot_id": "test_qq", "group_id": "654321"},
                    ],
                    "guild_list": [
                        {
                            "adapter": "qq",
                            "bot_id": "987654321",
                            "channel_id": "9876543210",
                        }
                    ],
                }
            }
        },
    }
