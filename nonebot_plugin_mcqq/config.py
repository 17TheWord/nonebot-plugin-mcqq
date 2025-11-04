"""
配置文件
"""

import importlib.util
import json
from pathlib import Path
from typing import Any

from nonebot import get_plugin_config, logger
from nonebot.compat import PYDANTIC_V2
from pydantic import BaseModel, Field

if PYDANTIC_V2:
    from pydantic import field_validator
else:
    from pydantic import validator

from .data_source import IGNORE_WORD_LIST


class Guild(BaseModel):
    """频道配置"""

    channel_id: str
    """子频道号"""
    adapter: str
    """适配器类型"""
    bot_id: str
    """Bot ID 优先使用所选Bot发送消息"""


class Group(BaseModel):
    """群配置"""

    group_id: str
    """群号"""
    adapter: str
    """适配器类型"""
    bot_id: str
    """Bot ID 优先使用所选Bot发送消息"""


class Server(BaseModel):
    """服务器配置"""

    group_list: list[Group] = []
    """群列表"""
    guild_list: list[Guild] = []
    """频道列表"""
    rcon_msg: bool = False
    """是否用Rcon发送消息"""


class MCQQConfig(BaseModel):
    """配置"""

    command_header: Any = {"mcc"}
    """命令头"""

    ignore_message_header: Any = {""}
    """忽略消息头"""

    ignore_word_file: str = "./src/mc_qq_ignore_word_list.json"
    """敏感词文件路径"""

    ignore_word_list: set[str] = set()
    """忽略的敏感词列表"""

    command_priority: int = 98
    """命令优先级，1-98，消息优先级=命令优先级 - 1"""

    command_block: bool = True
    """命令消息是否阻断后续消息"""

    notice_connected: bool = False
    """是否在服务器连接状态变化时发送通知"""

    rcon_result_to_image: bool = False
    """是否将 Rcon 命令执行结果转换为图片"""

    ttf_path: Path = Path(__file__).parent / "resource" / "unifont-15.0.01.ttf"
    """字体路径"""

    send_group_name: bool = False
    """是否发送群聊名称"""

    display_server_name: bool = False
    """是否发送服务器名称"""

    say_way: str = "："
    """用户发言修饰"""

    server_dict: dict[str, Server] = Field(default_factory=dict)
    """服务器配置"""

    guild_admin_roles: list[str] = ["频道主", "超级管理员"]
    """频道管理员角色"""

    chat_image_enable: bool = False
    """是否启用 ChatImage MOD"""

    cmd_whitelist: set[str] = {"list", "tps", "banlist"}
    """命令白名单"""

    auto_whitelist: bool = False
    """自动发放白名单"""

    @classmethod
    def _get_common_set(
        cls, v: Any, configuration_name: str, default_config: set = set()
    ):
        if isinstance(v, str):
            logger.info(f"{configuration_name} is a string, use it as is.")
            return {v}
        elif isinstance(v, list | set):
            logger.info(f"{configuration_name} is a list, loaded {len(v)} items.")
            return set(v)
        else:
            logger.warning(
                f"Invalid type for {configuration_name}: {type(v)}, use empty list."
            )
            return default_config

    @(
        field_validator("command_header", mode="before")
        if PYDANTIC_V2
        else validator("command_header", pre=True, always=True)
    )
    @classmethod
    def validate_command_header(cls, v: Any) -> set[str]:
        return cls._get_common_set(v, "command_header", {"mcqq"})

    @(
        field_validator("ignore_message_header", mode="before")
        if PYDANTIC_V2
        else validator("ignore_message_header", pre=True, always=True)
    )
    @classmethod
    def validate_ignore_message_header(cls, v: Any) -> set[str]:
        return cls._get_common_set(v, "ignore_message_header")

    @(
        field_validator("ignore_word_list", mode="before")
        if PYDANTIC_V2
        else validator("ignore_word_list", pre=True, always=True)
    )
    @classmethod
    def validate_ignore_word_list(cls, v: Any):
        return cls._get_common_set(v, "ignore_word_list")

    @(
        field_validator("command_priority", mode="before")
        if PYDANTIC_V2
        else validator("command_priority", pre=True, always=True)
    )
    @classmethod
    def validate_priority(cls, v: int) -> int:
        if 1 <= v <= 98:
            return v
        logger.warning("Invalid command_priority, use default 98.")
        return 98

    @(
        field_validator("rcon_result_to_image", mode="before")
        if PYDANTIC_V2
        else validator("rcon_result_to_image", pre=True, always=True)
    )
    @classmethod
    def validate_rcon_result_to_image(cls, v: bool) -> bool:
        is_pil_exists: bool = importlib.util.find_spec("PIL") is not None
        if v and not is_pil_exists:
            logger.warning(
                "Pillow not installed, please install it to use rcon result to image."
            )
            return False
        return v

    @(
        field_validator("ttf_path", mode="before")
        if PYDANTIC_V2
        else validator("ttf_path", pre=True, always=True)
    )
    @classmethod
    def validate_ttf_path(cls, v: str) -> Path:
        if v:
            if Path(v).exists():
                logger.info(f"ttf_path {v} exists, use it.")
                return Path(v)
            logger.warning(f"ttf_path {v} not exists, please check your config.")
        else:
            logger.warning("ttf_path not set, use default.")
        return Path(__file__).parent / "unifont-15.0.01.ttf"


class Config(BaseModel):
    """配置项"""

    mc_qq: MCQQConfig = MCQQConfig()


plugin_config = get_plugin_config(Config).mc_qq

if plugin_config.ignore_word_list:
    IGNORE_WORD_LIST.add(*plugin_config.ignore_word_list)
    logger.info("加载敏感词列表成功")
else:
    logger.info("敏感词列表为空，不加载")

if Path(plugin_config.ignore_word_file).exists():
    try:
        with open(plugin_config.ignore_word_file, encoding="utf-8") as f:
            json_data = json.load(f)
            words = json_data.get("words", [])
            if words:
                IGNORE_WORD_LIST.update(words)
                logger.info(f"加载敏感词文件成功，敏感词数量为 {len(words)}")
            else:
                logger.warning("敏感词文件为空，不加载")
    except Exception as e:
        logger.error(f"加载敏感词文件失败，请检查文件格式，错误信息为：{e}")
else:
    logger.info("敏感词文件不存在，不加载")
