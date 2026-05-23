---
description: "理解 nonebot-plugin-mcqq 项目架构、消息流、配置、测试与开发约定，并基于这些上下文协助开发"
name: "MCQQ Project Context"
argument-hint: "描述要在 nonebot-plugin-mcqq 中完成的任务"
agent: "agent"
---

# MCQQ Project Context

你正在协助维护 `nonebot-plugin-mcqq`。在回答问题、分析缺陷、编写代码或提出修改方案前，请先基于以下项目上下文理解仓库结构与既有约定。

## 项目概览

`nonebot-plugin-mcqq` 是一个基于 NoneBot2 的 QQ ↔ Minecraft 消息互通插件。

核心目标：

- 将 Minecraft 服务器聊天、玩家加入/退出、死亡、成就等事件同步到 QQ。
- 将 QQ 群聊、QQ 频道中的消息和命令同步到 Minecraft 服务器。
- 支持多个 Minecraft 服务器与多个群聊/频道的多对多绑定。

支持的适配器：

- `nonebot-adapter-minecraft`
- `nonebot-adapter-onebot`，用于 OneBot V11 QQ 群。
- `nonebot-adapter-qq`，用于 QQ 官方群 at 消息与 QQ 频道。

项目基本信息：

- Python 版本：`>=3.10,<4`
- 当前版本：`2.9.0`
- 构建后端：`hatchling`
- 核心框架：`nonebot2[fastapi,httpx,websockets]`
- 可选依赖：`pillow`，用于 RCON 结果转图片。

## 主要目录与文件

```text
nonebot_plugin_mcqq/
  __init__.py
  bot_manage.py
  config.py
  data_source.py
  on_minecraft_msg.py
  on_qq_msg.py
  resource/
  utils/
    __init__.py
    draw_result.py
    parse_qq_msg.py
    qq_util.py
    rule.py
    send_to_mc.py
    send_to_qq.py

tests/
  conftest.py
  test_bot_manage.py
  test_on_minecraft_msg.py
  test_on_qq_msg.py
```

## 核心模块职责

### `nonebot_plugin_mcqq/config.py`

负责插件配置模型与配置校验。

关键模型：

- `Guild`：QQ 频道配置，包含 `channel_id`、`adapter`、`bot_id`。
- `Group`：QQ群配置，包含 `group_id`、`adapter`、`bot_id`。
- `Server`：Minecraft 服务器配置，包含 `group_list`、`guild_list`、`rcon_msg`。
- `MCQQConfig`：插件主配置。
- `Config`：NoneBot 插件配置入口，字段为 `mc_qq`。

注意事项：

- 项目兼容 Pydantic v1/v2，使用 `nonebot.compat.PYDANTIC_V2` 分支导入 validator。
- `command_header`、`ignore_message_header`、`ignore_word_list` 支持字符串、列表或集合输入，最终转为 `set[str]`。
- `command_priority` 限制在 `1..98`。
- `rcon_result_to_image` 依赖 Pillow，不存在 `PIL` 时会自动关闭。
- 敏感词可来自 `mc_qq.ignore_word_list` 和 `mc_qq.ignore_word_file`。

### `nonebot_plugin_mcqq/data_source.py`

存放运行期全局映射数据。

重点数据结构：

- `ONEBOT_GROUP_SERVER_DICT`：OneBot 群号到 Minecraft server 列表的映射。
- `QQ_GROUP_SERVER_DICT`：QQ 官方群 openid 到 Minecraft server 列表的映射。
- `QQ_GUILD_SERVER_DICT`：QQ 子频道 ID 到 Minecraft server 列表的映射。
- `IGNORE_WORD_LIST`：敏感词集合。

修改消息路由、绑定关系或过滤逻辑时，应同步考虑这些映射。

### `nonebot_plugin_mcqq/bot_manage.py`

负责 Minecraft Bot 连接与断开生命周期。

典型职责：

- 在 Minecraft Bot 连接时维护群/频道与 server 的映射。
- 在 Minecraft Bot 断开时清理映射。
- 根据配置决定是否向 QQ 通知服务器连接状态变化。

### `nonebot_plugin_mcqq/on_qq_msg.py`

QQ 侧事件入口。

关键 matcher：

- `on_qq_msg`：普通 QQ/频道消息入口。
- `on_qq_cmd`：Minecraft RCON 命令入口，命令名为 `minecraft_command`，别名来自 `plugin_config.command_header`。
- `on_qq_send_title_cmd`：发送 Title，命令名 `mcst`。
- `on_qq_send_actionbar_cmd`：发送 ActionBar，命令名 `mcsa`。

关键 handler：

- `handle_qq_msg`
- `handle_qq_cmd`
- `handle_qq_title_cmd`
- `handle_qq_actionbar_cmd`

事件类型通常是以下联合类型：

- `OneBotGroupMessageEvent`
- `QQGroupAtMessageCreateEvent`
- `QQGuildMessageEvent`

Bot 类型通常是：

- `OneBot`
- `QQBot`

命令权限：

- 普通消息不做命令权限检查。
- `/mcc` 命令如果不在 `plugin_config.cmd_whitelist` 中，需要通过 `permission_check`。
- `mcst` 和 `mcsa` 始终需要通过 `permission_check`。

### `nonebot_plugin_mcqq/on_minecraft_msg.py`

Minecraft 侧事件入口。

关键 matcher：

- `on_mc_msg`：Minecraft 聊天消息。
- `on_mc_notice`：Minecraft 通知事件。

关键 handler：

- `handle_mc_msg`：处理 `PlayerChatEvent`。
- `handle_mc_death`：处理 `PlayerDeathEvent`。
- `handle_mc_notice`：处理 `PlayerJoinEvent`。
- `handle_mc_quit`：处理 `PlayerQuitEvent`。
- `handle_mc_otherevent`：处理 `PlayerAchievementEvent`。

注意：

- 玩家发言格式由 `plugin_config.say_way` 控制，默认是 `：`。
- `handle_mc_msg` 中硬编码忽略以 `!!` 开头的消息。
- MC 消息最终通过 `send_mc_msg_to_qq(server_name, msg)` 转发到 QQ。

### `nonebot_plugin_mcqq/utils/send_to_mc.py`

QQ → Minecraft 的核心发送层。

关键函数：

- `get_mc_bot(server_name)`：根据 server name 获取 Minecraft Bot。
- `get_server_list(event)`：根据 QQ/OneBot 事件获取绑定的 Minecraft server 列表。
- `for_each_server(event, handler)`：遍历目标服务器并执行处理逻辑。
- `send_message_to_target_server(bot, event)`：发送 QQ 普通消息到 MC。
- `send_command_to_target_server(event, command)`：通过 RCON 执行命令。
- `send_title_to_target_server(event, title_message)`：发送 Title。
- `send_actionbar_to_target_server(event, action_bar)`：发送 ActionBar。

通信方式：

- 当 `Server.rcon_msg` 为 `True` 时，使用 RCON 命令。
- 当 `Server.rcon_msg` 为 `False` 时，使用 Minecraft adapter 的 WebSocket API，例如 `send_msg`、`send_title`、`send_actionbar`。

### `nonebot_plugin_mcqq/utils/send_to_qq.py`

Minecraft → QQ 的核心发送层。

关键函数：

- `send_mc_msg_to_qq(server_name, result)`

行为：

- 会剥离 Minecraft 颜色码，例如 `&a`、`§a`。
- 如果 `plugin_config.display_server_name` 为 `True`，会在消息前加 `[server_name]`。
- OneBot 群消息通过 `send_group_msg` 发送。
- QQ 频道消息通过 `send_to_channel` 发送。
- QQ 官方群主动消息因平台限制当前未实现，相关代码被注释并记录 debug 日志。

### `nonebot_plugin_mcqq/utils/parse_qq_msg.py`

负责将 QQ/OneBot 消息转换为 Minecraft adapter 的 `Message`、`MessageSegment`、`Component`。

关键函数：

- `parse_qq_msg_to_component(bot, event)`
- `__parse_message_to_mc_message_segment(...)`
- `__process_reply_message(...)`
- `__create_hover_click_events(url, display_text)`

支持的消息类型：

- 文本
- 图片/附件
- 视频
- 分享
- OneBot `at`
- QQ `mention_user`
- QQ `mention_channel`
- QQ `mention_everyone`
- 表情
- 语音
- 未知类型兜底为 `[未知消息类型 ...]`

消息转换规则：

- 图片、视频、分享会生成可点击链接，使用 Minecraft `HoverEvent` 和 `ClickEvent`。
- 回复消息会生成悬浮展示的回复内容。
- 如果 `plugin_config.send_group_name` 为 `True`，会在 MC 消息前追加群聊名称。
- 如果 `plugin_config.chat_image_enable` 为 `True`，图片消息可转换为 ChatImage CICode。

### `nonebot_plugin_mcqq/utils/rule.py`

负责事件规则与权限判断。

关键函数和对象：

- `mc_msg_rule(event)`：判断 Minecraft 消息是否来自已配置服务器，并应用敏感词过滤。
- `all_msg_rule(event)`：判断 QQ/频道事件是否来自已绑定群或频道。
- `permission_check(matcher, bot, event)`：命令权限检查。
- `QQ_GUILD_ROLE_ADMIN`：QQ 频道身份组权限。

权限规则：

- OneBot 群：群管理员、群主或 NoneBot `SUPERUSER`。
- QQ 频道：频道管理员、频道主、`SUPERUSER` 或配置的 `guild_admin_roles` 身份组。
- QQ 官方群：默认仅 `SUPERUSER`。

### `nonebot_plugin_mcqq/utils/qq_util.py`

负责 QQ 平台辅助能力。

典型职责：

- 获取群名、昵称、频道名。
- 标准化 URL。
- 缓存群成员、频道、身份组等信息，减少重复 API 调用。

### `nonebot_plugin_mcqq/utils/draw_result.py`

负责将 RCON 执行结果渲染为图片。

注意：

- 依赖 Pillow。
- 与 `mc_qq.rcon_result_to_image`、`mc_qq.ttf_path` 配置相关。

## 关键消息流

### Minecraft → QQ

流程：

1. Minecraft adapter 产生事件，例如：
   - `PlayerChatEvent`
   - `PlayerDeathEvent`
   - `PlayerJoinEvent`
   - `PlayerQuitEvent`
   - `PlayerAchievementEvent`
2. `on_minecraft_msg.py` 中对应 handler 生成文本消息。
3. 调用 `send_mc_msg_to_qq(server_name, msg)`。
4. `send_to_qq.py` 根据 `plugin_config.server_dict[server_name]` 遍历：
   - `group_list`
   - `guild_list`
5. 根据适配器类型发送到 QQ：
   - OneBot 群：`send_group_msg`
   - QQ 频道：`send_to_channel`

### QQ → Minecraft

流程：

1. QQ/OneBot 产生事件：
   - `OneBotGroupMessageEvent`
   - `QQGroupAtMessageCreateEvent`
   - `QQGuildMessageEvent`
2. `all_msg_rule(event)` 判断该群/频道是否已绑定 Minecraft server。
3. `handle_qq_msg` 调用 `send_message_to_target_server(bot, event)`。
4. `get_server_list(event)` 根据事件类型读取绑定的 server 列表。
5. `for_each_server(event, handler)` 遍历目标 server。
6. `parse_qq_msg_to_component(bot, event)` 将 QQ 消息转换为 MC 消息组件。
7. 根据 `server.rcon_msg`：
   - `True`：使用 RCON `tellraw`。
   - `False`：使用 WebSocket API `send_msg`。

### QQ 命令 → Minecraft RCON

流程：

1. 用户发送命令，命令头来自 `plugin_config.command_header`，默认包含 `mcc`。
2. `handle_qq_cmd` 提取命令文本。
3. 如果命令不在 `plugin_config.cmd_whitelist`，先执行 `permission_check`。
4. 调用 `send_command_to_target_server(event, command)`。
5. 目标 Minecraft Bot 执行 `send_rcon_command(command=command)`。
6. RCON 结果通过 `get_rcon_result` 处理后返回 QQ。

### Title / ActionBar

流程：

1. 用户发送：
   - `mcst`：Title
   - `mcsa`：ActionBar
2. 通过 `permission_check`。
3. 调用：
   - `send_title_to_target_server`
   - `send_actionbar_to_target_server`
4. 根据 `server.rcon_msg` 使用 RCON 或 WebSocket API。

## 配置要点

根配置项是 `mc_qq`。

常用字段：

- `command_header`：命令触发词，默认类似 `mcc`。
- `ignore_message_header`：忽略消息前缀。
- `ignore_word_file`：敏感词文件路径。
- `ignore_word_list`：敏感词列表。
- `command_priority`：命令优先级，范围 `1..98`。
- `command_block`：命令是否阻断后续消息处理。
- `notice_connected`：服务器连接状态变化时是否通知 QQ。
- `rcon_result_to_image`：是否将 RCON 结果转图片。
- `ttf_path`：图片渲染字体路径。
- `send_group_name`：是否向 MC 发送群聊名称。
- `display_server_name`：是否向 QQ 消息追加服务器名。
- `say_way`：发言分隔符，默认 `：`。
- `server_dict`：服务器绑定配置。
- `guild_admin_roles`：QQ 频道管理员身份组名称列表。
- `chat_image_enable`：是否启用 ChatImage MOD 图片展示格式。
- `cmd_whitelist`：无需权限检查的命令白名单。

`server_dict` 结构概念：

```yaml
mc_qq:
  server_dict:
    <server_name>:
      group_list:
        - adapter: "onebot"
          bot_id: "<bot_id>"
          group_id: "<group_id>"
        - adapter: "qq"
          bot_id: "<bot_id>"
          group_id: "<group_openid>"
      guild_list:
        - adapter: "qq"
          bot_id: "<bot_id>"
          channel_id: "<channel_id>"
      rcon_msg: false
```

## 开发约定

处理代码修改时请遵循以下约定：

1. 优先复用现有分层：
   - 事件入口：`on_qq_msg.py`、`on_minecraft_msg.py`
   - 发送逻辑：`utils/send_to_mc.py`、`utils/send_to_qq.py`
   - 消息解析：`utils/parse_qq_msg.py`
   - 规则和权限：`utils/rule.py`
   - 平台辅助：`utils/qq_util.py`

2. 保持异步风格：
   - NoneBot handler、Bot API、网络/IO 相关工具函数应使用 `async/await`。

3. 多适配器逻辑应显式区分类型：
   - `OneBotGroupMessageEvent`
   - `QQGroupAtMessageCreateEvent`
   - `QQGuildMessageEvent`
   - `OneBot`
   - `QQBot`

4. 修改绑定或路由时检查这些映射：
   - `ONEBOT_GROUP_SERVER_DICT`
   - `QQ_GROUP_SERVER_DICT`
   - `QQ_GUILD_SERVER_DICT`

5. 修改 QQ → MC 消息格式时，优先在 `parse_qq_msg_to_component` 及其私有辅助函数中扩展。

6. 修改 MC → QQ 消息格式时，优先检查 `send_mc_msg_to_qq`。

7. 命令权限不要绕过 `permission_check`；如新增命令，应明确是否允许 `cmd_whitelist` 或是否必须管理员权限。

8. 日志建议沿用现有前缀：`[MC_QQ]丨`。

9. 注意 QQ 官方群主动消息限制：`send_to_qq.py` 中 QQ 群主动发送当前未实现，不要误以为该路径已可用。

10. 代码风格遵循 `pyproject.toml` 中 Ruff 配置：
    - 行宽：`88`
    - Python target：`py310`
    - 双引号
    - import 排序遵循 Ruff/isort 配置

## 测试与验证

测试栈：

- `pytest`
- `pytest-asyncio`
- `pytest-cov`
- `nonebug`

测试初始化位于 `tests/conftest.py`：

- 注册 Minecraft、OneBot V11、QQ adapter。
- 通过 `NONEBOT_INIT_KWARGS` 配置测试环境。
- 测试服务器名：`test_server`。
- 测试映射包含 OneBot 群、QQ 群和 QQ 频道。

现有测试文件：

- `tests/test_bot_manage.py`
- `tests/test_on_minecraft_msg.py`
- `tests/test_on_qq_msg.py`

推荐验证命令：

- `uv run pytest`
- `uv run ruff check .`
- `uv run ruff format --check .`

如果当前环境未使用 `uv`，请使用项目虚拟环境中的等价 `pytest` 和 `ruff` 命令。

## 回答与执行要求

当用户基于本 Prompt 请求帮助时：

1. 先判断任务涉及的模块和消息流。
2. 优先检索并遵循既有实现模式，不要重写已有架构。
3. 回答中尽量引用具体文件、函数、配置项。
4. 如需修改代码，保持现有异步风格和多适配器兼容性。
5. 如新增功能，考虑是否需要同步修改配置、规则、测试。
6. 如修改消息路由、权限或格式转换，说明对 QQ → MC 与 MC → QQ 两个方向的影响。
7. 修改完成后建议或执行相关测试。
