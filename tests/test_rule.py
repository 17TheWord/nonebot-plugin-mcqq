import time
import uuid

from nonebot.adapters.minecraft import Message as MinecraftMessage
from nonebot.adapters.minecraft import Player, PlayerChatEvent
import pytest

from tests.test_on_qq_msg import (
    make_onebot_group_message_event,
    make_qq_group_message_event,
    make_qq_guild_message_event,
)


@pytest.fixture(autouse=True)
def reset_rule_state(app):
    from nonebot_plugin_mcqq.config import plugin_config
    from nonebot_plugin_mcqq.data_source import (
        IGNORE_WORD_LIST,
        ONEBOT_GROUP_SERVER_DICT,
        QQ_GROUP_SERVER_DICT,
        QQ_GUILD_SERVER_DICT,
    )

    old_ignore_word_list = plugin_config.ignore_word_list
    old_ignore_words = set(IGNORE_WORD_LIST)
    old_onebot_mapping = dict(ONEBOT_GROUP_SERVER_DICT)
    old_qq_group_mapping = dict(QQ_GROUP_SERVER_DICT)
    old_qq_guild_mapping = dict(QQ_GUILD_SERVER_DICT)
    yield
    plugin_config.ignore_word_list = old_ignore_word_list
    IGNORE_WORD_LIST.clear()
    IGNORE_WORD_LIST.update(old_ignore_words)
    ONEBOT_GROUP_SERVER_DICT.clear()
    ONEBOT_GROUP_SERVER_DICT.update(old_onebot_mapping)
    QQ_GROUP_SERVER_DICT.clear()
    QQ_GROUP_SERVER_DICT.update(old_qq_group_mapping)
    QQ_GUILD_SERVER_DICT.clear()
    QQ_GUILD_SERVER_DICT.update(old_qq_guild_mapping)


def make_mc_chat_event(server_name: str, message: str):
    return PlayerChatEvent(
        server_name=server_name,
        server_version="test_version",
        server_type="test_type",
        timestamp=int(time.time()),
        player=Player(uuid=uuid.uuid4(), nickname="test_player"),
        event_name="PlayerChatEvent",
        post_type="message",
        sub_type="player_chat",
        message=MinecraftMessage(message),
    )


def test_all_msg_rule_accepts_bound_events(app):
    from nonebot_plugin_mcqq.data_source import (
        ONEBOT_GROUP_SERVER_DICT,
        QQ_GROUP_SERVER_DICT,
        QQ_GUILD_SERVER_DICT,
    )
    from nonebot_plugin_mcqq.utils.rule import all_msg_rule

    ONEBOT_GROUP_SERVER_DICT["1234567890"] = ["test_server"]
    QQ_GROUP_SERVER_DICT["654321"] = ["test_server"]
    QQ_GUILD_SERVER_DICT["9876543210"] = ["test_server"]

    assert all_msg_rule(make_onebot_group_message_event("hello")) is True
    assert all_msg_rule(make_qq_group_message_event("hello")) is True
    assert all_msg_rule(make_qq_guild_message_event("hello")) is True


def test_all_msg_rule_rejects_unbound_events(app):
    from nonebot_plugin_mcqq.data_source import (
        ONEBOT_GROUP_SERVER_DICT,
        QQ_GROUP_SERVER_DICT,
        QQ_GUILD_SERVER_DICT,
    )
    from nonebot_plugin_mcqq.utils.rule import all_msg_rule

    ONEBOT_GROUP_SERVER_DICT.clear()
    QQ_GROUP_SERVER_DICT.clear()
    QQ_GUILD_SERVER_DICT.clear()

    assert all_msg_rule(make_onebot_group_message_event("hello")) is False
    assert all_msg_rule(make_qq_group_message_event("hello")) is False
    assert all_msg_rule(make_qq_guild_message_event("hello")) is False


def test_mc_msg_rule_checks_configured_server_without_ignore_words(app):
    from nonebot_plugin_mcqq.config import plugin_config
    from nonebot_plugin_mcqq.utils.rule import mc_msg_rule

    plugin_config.ignore_word_list = set()

    assert mc_msg_rule(make_mc_chat_event("test_server", "hello")) is True
    assert mc_msg_rule(make_mc_chat_event("missing_server", "hello")) is False


def test_mc_msg_rule_filters_ignore_words_when_configured(app):
    from nonebot_plugin_mcqq.config import plugin_config
    from nonebot_plugin_mcqq.data_source import IGNORE_WORD_LIST
    from nonebot_plugin_mcqq.utils.rule import mc_msg_rule

    plugin_config.ignore_word_list = {"bad"}
    IGNORE_WORD_LIST.clear()
    IGNORE_WORD_LIST.add("bad")

    assert mc_msg_rule(make_mc_chat_event("missing_server", "hello")) is True
    assert mc_msg_rule(make_mc_chat_event("missing_server", "bad message")) is False
