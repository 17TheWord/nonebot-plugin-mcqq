# nonebot-plugin-msgqq

基于 `NoneBot` 的与 `Minecraft Server` 互通消息插件

支持QQ群、QQ频道

# 使用说明

## 环境
- `Python 3.10.5`
  - `websockets 10.3`


- `nb-cli 0.6.7`
  - `nonebot-adapter-onebot 2.1.1`
  - `nonebot2 2.0.0b4`
  - `nonebot-plugin-guild-patch`


- `OpenJDK 17`


- `Minecraft 1.18.1`


- `Spigot 1.18.1`

## 功能

- 推送消息列表：
  - 服务器 -> QQ：
    - 加入 / 离开 服务器消息
    - 玩家聊天信息
  - QQ -> 服务器：
    - 群员聊天文本
    - 图片、视频等内容转换为 `[图片]`、`[视频]`

- 特殊消息支持
  - 群聊
    - [x] @ 消息
    - [x] 回复消息
  - 频道
    - [ ] @ 消息
    - [ ] 回复消息
  - 未支持的消息已被替换，如： `[图片]`、 `[视频]` 等等

## 安装
### NoneBot
- 下载 `nonebot-plugin-guild-patch`、`nonebot_plugin_msgqq` 到 `plugins` 文件夹
- 下载 `msg_qq_config.py` 到 `src` 目录
  - 或复制以下参考内容自行在 `src` 文件夹内新建 `msg_qq_config.py` 文件

```python
# 在此填入 WebSocket 地址
# 一般修改只修改端口号
ws_url = "ws://localhost:8765"

# 开启功能的群和频道列表
group_list = {
    # 群列表
    "group_list": [
        # 群号
        123456789,
    ],
    # 频道列表
    "guild_list": [
        {
            # 频道 ID
            "guild_id": 12345678909876543,
            # 子频道 ID
            "channel_id": 1234567,
        },
    ],
}

```

- 目录结构参考：  

```
📦 test_bot
├── 📂 plugins
│   ├── 📂 nonebot_plugin_msgqq      # msgqq 插件
│   └── 📂 nonebot_plugin_guild_patch        # 频道适配插件
├── 📂 src                 # 或是 test_bot
│   └── 📜 msg_qq_config.py
├── 📜 .env                # 可选的
├── 📜 .env.dev            # 可选的
├── 📜 .env.prod           # 可选的
├── 📜 .gitignore
├── 📜 bot.py
├── 📜 docker-compose.yml
├── 📜 Dockerfile
├── 📜 pyproject.toml
└── 📜 README.md
```

### Minecraft Server

- 将 `Msg_QQ.jar` 放入 `Minecraft` 服务器 `plugins` 文件夹
- 启动服务器后插件将自动生成配置文件并写入默认信息
- 参考如下

```yaml
# 是否启用插件
# 默认为 true
enable_msg_qq: true

# 请在冒号后填写 WebSocket 服务的地址端口号。
# 只填写数字即可。
# 冒号后需要空一格！
# 若不填写，则地址默认为 0.0.0.0 ，端口默认为 8765
websocket_server:
  address: "0.0.0.0"
  port: "8765"

# 发送到群消息中，玩家昵称与消息之间的符号
# 默认为中文冒号 “：”
# 例如：
#   17TheWord ： 你好
say_way: "说："

# 是否启用 加入/离开 服务器监听
# 开启后，当玩家 加入/离开 服务器时，Bot会随推送信息
# 默认打开
# 例如：
#   17TheWord 加入了服务器
#   17TheWord 离开了服务器
join_quit: true
```

如果一切顺利的话，到这里你的消息互通已经搭建完成了。

## 特别感谢
- [@SK-415](https://github.com/SK-415) ：感谢SK佬给予许多优秀的建议和耐心的解答。
- [@zhz-红石头](https://github.com/zhzhongshi) ：感谢红石头在代码上的帮助
- [NoneBot2](https://github.com/nonebot/nonebot2)： 插件使用的开发框架。
- [go-cqhttp](https://github.com/Mrs4s/go-cqhttp)： 稳定完善的 CQHTTP 实现。
