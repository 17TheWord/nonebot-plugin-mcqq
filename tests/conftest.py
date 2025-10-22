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
    config.stash[NONEBOT_INIT_KWARGS] = {
        "driver": "~fastapi+~websockets+~httpx",
        "minecraft_access_token": "test_access_token",
        "mc_qq": {
            "server_dict": {
                "test_server": {
                    "group_list": [
                        {
                            "adapter": "onebot",
                            "bot_id": "test_onebot",
                            "group_id": "123456",
                        },
                        {"adapter": "qq", "bot_id": "test_qq", "group_id": "654321"},
                    ],
                    "guild_list": [
                        {"adapter": "qq", "bot_id": "test_qq", "channel_id": "789012"}
                    ],
                }
            }
        },
    }
