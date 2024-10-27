[![nonebot-plugin-mcqq](https://socialify.git.ci/17TheWord/nonebot-plugin-mcqq/image?description=1&forks=1&issues=1&language=1&logo=https%3A%2F%2Fraw.githubusercontent.com%2F17TheWord%2Fnonebot-adapter-minecraft%2Fmain%2Fassets%2Flogo.png&name=1&owner=1&pulls=1&stargazers=1&theme=Auto)](https://github.com/17TheWord/nonebot-plugin-mcqq)

# NoneBot-Plugin-MCQQ

基于 `NoneBot` 的与 `Minecraft Server` 互通消息插件

- 支持 QQ 群、QQ 频道
- 支持多个服务器与多个群聊的互通

# 文档

- [简陋的 Wiki](https://github.com/17TheWord/nonebot-plugin-mcqq/wiki)

# 支持的服务端列表

- Spigot
- Forge
- Fabric
- Velocity
- 原版端

配套 **插件/模组** 请前往 [`鹊桥`](https://github.com/17TheWord/QueQiao) 仓库查看详情

# 功能

- 推送消息列表

  - 服务器 -> QQ
    - [x] 加入 / 离开 服务器消息
    - [x] 玩家聊天信息
    - [x] 玩家死亡信息（死亡信息为英文，原版端不适用，用**正则**匹配死亡信息是大工程！）
  - QQ -> 服务器
    - [x] 指令
    - [x] 群员聊天文本
    - [x] 图片、视频等内容转换为可点击在浏览器打开的 `[图片]`、`[视频]`
    - [x] 可选配置，借助 [`@kitUIN/ChatImage`](https://github.com/kitUIN/ChatImage) 直接在游戏内显示图片

- 特殊消息支持
  - 群聊
    - [x] @ 消息
    - [x] 回复消息（转换成@消息）
  - 频道
    - [x] @ 消息
    - [x] 回复消息（转换成@消息）
  - 未支持的消息已被替换，如： `[msgType]` 等等

# 特别感谢

- [@SK-415](https://github.com/SK-415)：感谢 SK 佬给予许多优秀的建议和耐心的解答。
- [@zhz-红石头](https://github.com/zhzhongshi)：感谢红石头在代码上的帮助
- [NoneBot2](https://github.com/nonebot/nonebot2)：插件使用的开发框架。
- [go-cqhttp](https://github.com/Mrs4s/go-cqhttp)：稳定完善的 CQHTTP 实现。

# 二创

- [@KarisAya/mcqq 服主版](https://github.com/KarisAya/nonebot_plugin_mcqq_server)：采用本地读取 log 信息的方法的 Minecraft Server 互通消息的插件
- [@CikeyQi/mc-plugin](https://github.com/CikeyQi/mc-plugin)：适用于 `Yunzai` 的互通消息插件

# 关于 Minecraft 适配器

- 本插件基于 [`nonebot-adapter-minecraft`](https://github.com/17TheWord/nonebot-adapter-minecraft) 适配器实现 `Websocket`、`Rcon` 通信
- 若有自定义一些简单插件的想法，可以一试，例如：
  - 非插件端无权限系统场景下实现普通玩家使用`tp`命令
  - 实现简单的自助领取游戏物品

# 贡献与支持

觉得好用可以给这个项目点个 `Star` 或者去 [爱发电](https://afdian.net/a/17TheWord) 投喂我。

有意见或者建议也欢迎提交 [Issues](https://github.com/17TheWord/nonebot-plugin-mcqq/issues)
和 [Pull requests](https://github.com/17TheWord/nonebot-plugin-mcqq/pulls)。

# 许可证

本项目使用 [MIT](./LICENSE) 作为开源许可证。
