from collections import defaultdict

IGNORE_WORD_LIST: set[str] = set()
"""忽略的敏感词列表"""

ONEBOT_GROUP_SERVER_DICT: dict[str, list[str]] = defaultdict(list)
"""OneBot 群服映射"""

QQ_GROUP_SERVER_DICT: dict[str, list[str]] = defaultdict(list)
"""QQ 适配器群服映射"""

QQ_GUILD_SERVER_DICT: dict[str, list[str]] = defaultdict(list)
"""QQ 适配器频道映射"""
