import nonebot
from nonebot.adapters.onebot.v11 import Adapter as OneBotAdapter
from nonebot.adapters.onebot.v11 import Bot as OneBot
from nonebot.adapters.qq import Adapter as QQAdapter
from nonebot.adapters.qq import Bot as QQBot
from nonebot.adapters.qq.config import BotInfo
from nonebot.adapters.qq.models import Channel, Guild
from nonebug import App
import pytest

from tests.test_on_qq_msg import (
    make_onebot_group_message_event,
    make_qq_group_message_event,
    make_qq_guild_message_event,
)


@pytest.fixture(autouse=True)
def clear_qq_util_caches(app: App):
    from nonebot_plugin_mcqq.utils.qq_util import (
        ONEBOT_GROUP_MEMBER_NICKNAME_CACHE,
        ONEBOT_GROUP_NAME_CACHE,
        QQ_CHANNEL_NAME_CACHE,
        QQ_GUILD_MEMBER_NICKNAME_CACHE,
        QQ_GUILD_NAME_CACHE,
    )

    ONEBOT_GROUP_MEMBER_NICKNAME_CACHE.clear()
    ONEBOT_GROUP_NAME_CACHE.clear()
    QQ_CHANNEL_NAME_CACHE.clear()
    QQ_GUILD_MEMBER_NICKNAME_CACHE.clear()
    QQ_GUILD_NAME_CACHE.clear()


def test_normalize_url_adds_https_only_when_needed():
    from nonebot_plugin_mcqq.utils.qq_util import normalize_url

    assert normalize_url("example.com/image.png") == "https://example.com/image.png"
    assert normalize_url("http://example.com") == "http://example.com"
    assert normalize_url("https://example.com") == "https://example.com"


@pytest.mark.asyncio
async def test_get_onebot_group_and_member_names(app: App):
    from nonebot_plugin_mcqq.utils.qq_util import get_group_or_nick_name

    async with app.test_api() as ctx:
        bot = ctx.create_bot(
            base=OneBot,
            adapter=nonebot.get_adapter(OneBotAdapter),
            self_id="123456789",
        )
        event = make_onebot_group_message_event("hello")

        assert await get_group_or_nick_name(bot, event, "111111111") == "TestUser"

        ctx.should_call_api(
            api="get_group_info",
            data={"group_id": 1234567890},
            result={"group_name": "TestGroup"},
        )
        assert await get_group_or_nick_name(bot, event) == "TestGroup"
        assert await get_group_or_nick_name(bot, event) == "TestGroup"

        ctx.should_call_api(
            api="get_group_member_info",
            data={"group_id": 1234567890, "user_id": 222222222, "no_cache": True},
            result={"nickname": "OtherUser"},
        )
        assert await get_group_or_nick_name(bot, event, "222222222") == "OtherUser"
        assert await get_group_or_nick_name(bot, event, "222222222") == "OtherUser"


@pytest.mark.asyncio
async def test_get_qq_group_name_and_member_fallback(app: App):
    from nonebot_plugin_mcqq.utils.qq_util import get_group_or_nick_name

    async with app.test_api() as ctx:
        bot_info = BotInfo(id="test_qq", token="test_token", secret="test_secret")
        bot = ctx.create_bot(
            base=QQBot,
            adapter=nonebot.get_adapter(QQAdapter),
            self_id="test_qq",
            bot_info=bot_info,
        )
        event = make_qq_group_message_event("hello")

        assert await get_group_or_nick_name(bot, event) == "654321"
        assert await get_group_or_nick_name(bot, event, "111111111") == "TestUser"
        assert (
            await get_group_or_nick_name(bot, event, "other_openid") == "other_openid"
        )


@pytest.mark.asyncio
async def test_get_qq_channel_and_guild_names_are_cached(app: App):
    from nonebot_plugin_mcqq.utils.qq_util import (
        get_group_or_nick_name,
        get_qq_channel_name,
    )

    async with app.test_api() as ctx:
        bot_info = BotInfo(id="987654321", token="test_token", secret="test_secret")
        bot = ctx.create_bot(
            base=QQBot,
            adapter=nonebot.get_adapter(QQAdapter),
            self_id="987654321",
            bot_info=bot_info,
        )
        event = make_qq_guild_message_event("hello")

        ctx.should_call_api(
            api="get_channel",
            data={"channel_id": "9876543210"},
            result=Channel(
                id="9876543210",
                guild_id="2001",
                name="General",
                type=0,
                sub_type=0,
                position=1,
            ),
        )
        assert await get_qq_channel_name(bot, "9876543210") == "General"
        assert await get_qq_channel_name(bot, "9876543210") == "General"

        ctx.should_call_api(
            api="get_guild",
            data={"guild_id": "2001"},
            result=Guild(
                id="2001",
                name="Guild",
                icon="",
                owner_id="owner",
                owner=False,
                member_count=1,
                max_members=100,
                description="",
                joined_at="2024-01-01T00:00:00+00:00",
            ),
        )
        assert await get_group_or_nick_name(bot, event) == "[Guild/General]"
        assert await get_group_or_nick_name(bot, event) == "[Guild/General]"
