from nonebot.adapters.minecraft.exception import ActionFailed
from nonebot.adapters.qq import Message as QQMessage
from nonebug import App
import pytest

from tests.test_on_qq_msg import (
    make_onebot_group_message_event,
    make_qq_group_message_event,
    make_qq_guild_message_event,
)


class FakeMcBot:
    def __init__(self):
        self.commands: list[str] = []

    async def send_rcon_command(self, command: str):
        self.commands.append(command)
        return {
            "list": "&aGreen §cRed",
            'title @a title ["Title"]': "title ok",
            'title @a subtitle ["Subtitle"]': "subtitle ok",
            "title @a actionbar ['Action Bar']": "actionbar ok",
        }[command]

    async def send_title(self, title: str, subtitle: str):
        raise ActionFailed(message="title failed")

    async def send_actionbar(self, message: str):
        raise ActionFailed(message="actionbar failed")


@pytest.fixture(autouse=True)
def reset_send_to_mc_state(app):
    from nonebot_plugin_mcqq.config import plugin_config
    from nonebot_plugin_mcqq.data_source import (
        ONEBOT_GROUP_SERVER_DICT,
        QQ_GROUP_SERVER_DICT,
        QQ_GUILD_SERVER_DICT,
    )

    old_server_dict = dict(plugin_config.server_dict)
    old_rcon_msg = {
        server_name: server.rcon_msg
        for server_name, server in plugin_config.server_dict.items()
    }
    old_onebot_mapping = dict(ONEBOT_GROUP_SERVER_DICT)
    old_qq_group_mapping = dict(QQ_GROUP_SERVER_DICT)
    old_qq_guild_mapping = dict(QQ_GUILD_SERVER_DICT)
    yield
    plugin_config.server_dict.clear()
    plugin_config.server_dict.update(old_server_dict)
    for server_name, rcon_msg in old_rcon_msg.items():
        if server := plugin_config.server_dict.get(server_name):
            server.rcon_msg = rcon_msg
    ONEBOT_GROUP_SERVER_DICT.clear()
    ONEBOT_GROUP_SERVER_DICT.update(old_onebot_mapping)
    QQ_GROUP_SERVER_DICT.clear()
    QQ_GROUP_SERVER_DICT.update(old_qq_group_mapping)
    QQ_GUILD_SERVER_DICT.clear()
    QQ_GUILD_SERVER_DICT.update(old_qq_guild_mapping)


def test_get_server_list_returns_bound_servers(app):
    from nonebot_plugin_mcqq.data_source import (
        ONEBOT_GROUP_SERVER_DICT,
        QQ_GROUP_SERVER_DICT,
        QQ_GUILD_SERVER_DICT,
    )
    from nonebot_plugin_mcqq.utils.send_to_mc import get_server_list

    ONEBOT_GROUP_SERVER_DICT["1234567890"] = ["test_server"]
    QQ_GROUP_SERVER_DICT["654321"] = ["test_server"]
    QQ_GUILD_SERVER_DICT["9876543210"] = ["test_server"]

    assert get_server_list(make_onebot_group_message_event("hello")) == ["test_server"]
    assert get_server_list(make_qq_group_message_event("hello")) == ["test_server"]
    assert get_server_list(make_qq_guild_message_event("hello")) == ["test_server"]


@pytest.mark.asyncio
async def test_for_each_server_reports_missing_bot(app: App):
    from nonebot_plugin_mcqq.data_source import ONEBOT_GROUP_SERVER_DICT
    from nonebot_plugin_mcqq.utils.send_to_mc import for_each_server

    ONEBOT_GROUP_SERVER_DICT["1234567890"] = ["missing_server"]

    async def handler(server_name, server, mc_bot):
        return f"handled {server_name}"

    result = await for_each_server(make_onebot_group_message_event("hello"), handler)

    assert result.extract_plain_text() == "服务器 missing_server 未连接"


@pytest.mark.asyncio
async def test_for_each_server_reports_missing_config(app: App, monkeypatch):
    from nonebot_plugin_mcqq.config import plugin_config
    from nonebot_plugin_mcqq.data_source import ONEBOT_GROUP_SERVER_DICT
    import nonebot_plugin_mcqq.utils.send_to_mc as send_to_mc

    ONEBOT_GROUP_SERVER_DICT["1234567890"] = ["configured_later"]
    plugin_config.server_dict.pop("configured_later", None)
    monkeypatch.setattr(send_to_mc, "get_mc_bot", lambda server_name: FakeMcBot())

    async def handler(server_name, server, mc_bot):
        return f"handled {server_name}"

    result = await send_to_mc.for_each_server(
        make_onebot_group_message_event("hello"), handler
    )

    assert result.extract_plain_text() == "服务器 configured_later 未配置"


@pytest.mark.asyncio
async def test_send_command_to_target_server_cleans_rcon_result(app: App, monkeypatch):
    from nonebot_plugin_mcqq.data_source import ONEBOT_GROUP_SERVER_DICT
    import nonebot_plugin_mcqq.utils.send_to_mc as send_to_mc

    ONEBOT_GROUP_SERVER_DICT["1234567890"] = ["test_server"]
    fake_bot = FakeMcBot()
    monkeypatch.setattr(send_to_mc, "get_mc_bot", lambda server_name: fake_bot)

    result = await send_to_mc.send_command_to_target_server(
        event=make_onebot_group_message_event("/minecraft_command list"),
        command="list",
    )

    assert result.extract_plain_text() == "[test_server] Green Red"
    assert fake_bot.commands == ["list"]


@pytest.mark.asyncio
async def test_send_title_to_target_server_uses_rcon_for_title_and_subtitle(
    app: App, monkeypatch
):
    from nonebot_plugin_mcqq.config import plugin_config
    from nonebot_plugin_mcqq.data_source import ONEBOT_GROUP_SERVER_DICT
    import nonebot_plugin_mcqq.utils.send_to_mc as send_to_mc

    ONEBOT_GROUP_SERVER_DICT["1234567890"] = ["test_server"]
    plugin_config.server_dict["test_server"].rcon_msg = True
    fake_bot = FakeMcBot()
    monkeypatch.setattr(send_to_mc, "get_mc_bot", lambda server_name: fake_bot)

    result = await send_to_mc.send_title_to_target_server(
        event=make_onebot_group_message_event("/mcst Title\nSubtitle", True),
        title_message="Title\nSubtitle",
    )

    assert result.extract_plain_text() == "title ok subtitle ok"
    assert fake_bot.commands == [
        'title @a title ["Title"]',
        'title @a subtitle ["Subtitle"]',
    ]


@pytest.mark.asyncio
async def test_send_actionbar_to_target_server_uses_rcon(app: App, monkeypatch):
    from nonebot_plugin_mcqq.config import plugin_config
    from nonebot_plugin_mcqq.data_source import ONEBOT_GROUP_SERVER_DICT
    import nonebot_plugin_mcqq.utils.send_to_mc as send_to_mc

    ONEBOT_GROUP_SERVER_DICT["1234567890"] = ["test_server"]
    plugin_config.server_dict["test_server"].rcon_msg = True
    fake_bot = FakeMcBot()
    monkeypatch.setattr(send_to_mc, "get_mc_bot", lambda server_name: fake_bot)

    result = await send_to_mc.send_actionbar_to_target_server(
        event=make_onebot_group_message_event("/mcsa Action Bar", True),
        action_bar="Action Bar",
    )

    assert result.extract_plain_text() == "actionbar ok"
    assert fake_bot.commands == ["title @a actionbar ['Action Bar']"]


@pytest.mark.asyncio
async def test_send_command_to_target_server_returns_qq_message(app: App, monkeypatch):
    from nonebot_plugin_mcqq.data_source import QQ_GROUP_SERVER_DICT
    import nonebot_plugin_mcqq.utils.send_to_mc as send_to_mc

    class QQFakeMcBot(FakeMcBot):
        async def send_rcon_command(self, command: str):
            self.commands.append(command)
            return "test"

    fake_bot = QQFakeMcBot()
    QQ_GROUP_SERVER_DICT["654321"] = ["test_server"]
    monkeypatch.setattr(send_to_mc, "get_mc_bot", lambda server_name: fake_bot)

    result = await send_to_mc.send_command_to_target_server(
        event=make_qq_group_message_event("/minecraft_command list"),
        command="list",
    )

    assert result == QQMessage("[test_server] test")
    assert fake_bot.commands == ["list"]


@pytest.mark.asyncio
async def test_send_title_to_target_server_reports_action_failed(app: App, monkeypatch):
    from nonebot_plugin_mcqq.config import plugin_config
    from nonebot_plugin_mcqq.data_source import ONEBOT_GROUP_SERVER_DICT
    import nonebot_plugin_mcqq.utils.send_to_mc as send_to_mc

    ONEBOT_GROUP_SERVER_DICT["1234567890"] = ["test_server"]
    plugin_config.server_dict["test_server"].rcon_msg = False
    monkeypatch.setattr(send_to_mc, "get_mc_bot", lambda server_name: FakeMcBot())

    result = await send_to_mc.send_title_to_target_server(
        event=make_onebot_group_message_event("/mcst Title", True),
        title_message="Title",
    )

    assert result.extract_plain_text() == "[test_server]发送 Title 失败：title failed"


@pytest.mark.asyncio
async def test_send_actionbar_to_target_server_reports_action_failed(
    app: App, monkeypatch
):
    from nonebot_plugin_mcqq.config import plugin_config
    from nonebot_plugin_mcqq.data_source import ONEBOT_GROUP_SERVER_DICT
    import nonebot_plugin_mcqq.utils.send_to_mc as send_to_mc

    ONEBOT_GROUP_SERVER_DICT["1234567890"] = ["test_server"]
    plugin_config.server_dict["test_server"].rcon_msg = False
    monkeypatch.setattr(send_to_mc, "get_mc_bot", lambda server_name: FakeMcBot())

    result = await send_to_mc.send_actionbar_to_target_server(
        event=make_onebot_group_message_event("/mcsa Action Bar", True),
        action_bar="Action Bar",
    )

    assert (
        result.extract_plain_text()
        == "[test_server]发送 ActionBar 失败：actionbar failed"
    )


@pytest.mark.asyncio
async def test_send_message_to_target_server_uses_rcon(app: App, monkeypatch):
    from nonebot_plugin_mcqq.config import plugin_config
    from nonebot_plugin_mcqq.data_source import ONEBOT_GROUP_SERVER_DICT
    import nonebot_plugin_mcqq.utils.send_to_mc as send_to_mc

    class RconMessageBot(FakeMcBot):
        async def send_rcon_command(self, command: str):
            self.commands.append(command)
            return "ok"

    fake_bot = RconMessageBot()
    ONEBOT_GROUP_SERVER_DICT["1234567890"] = ["test_server"]
    plugin_config.server_dict["test_server"].rcon_msg = True
    monkeypatch.setattr(send_to_mc, "get_mc_bot", lambda server_name: fake_bot)

    result = await send_to_mc.send_message_to_target_server(
        bot=object(),
        event=make_onebot_group_message_event("hello"),
    )

    assert result.extract_plain_text() == "已发送到服务器 test_server"
    assert fake_bot.commands == ['tellraw @a "[鹊桥] 未知名称 ：hello "']
