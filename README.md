[![nonebot-plugin-mcqq](https://socialify.git.ci/17TheWord/nonebot-plugin-mcqq/image?description=1&font=Inter&forks=1&issues=1&language=1&logo=https%3A%2F%2Favatars.githubusercontent.com%2F17TheWord&owner=1&pattern=Plus&stargazers=1&theme=Dark)](https://17theword.github.io/mc_qq/)

# NoneBot-Plugin-MCQQ

基于 `NoneBot` 的与 `Minecraft Server` 互通消息插件

- 支持QQ群、QQ频道
- 支持多个服务器与多个群聊的互通

# 文档

- [简陋的Wiki](https://github.com/17TheWord/nonebot-plugin-mcqq/wiki)

# 支持的服务端列表

- Spigot API
    - `MC_QQ_Spigot_XXX.jar` + `nonebot-plugin-mcqq`
- MinecraftServer
    - `MC_QQ_Minecraft_Server` + `nonebot-plugin-mcqq`
- ForgeServer
    - `MC_QQ_Minecraft_Server` + `nonebot-plugin-mcqq`
- Fabric
    - `MC_QQ_Minecraft_Server` + `nonebot-plugin-mcqq`

# 功能

- 推送消息列表
    - 服务器 -> QQ
        - [x] 加入 / 离开 服务器消息
        - [x] 玩家聊天信息
        - [x] 玩家死亡信息（死亡信息为英文，非插件服务端不适用。）
    - QQ -> 服务器
        - [x] 指令
        - [x] 群员聊天文本
        - [x] 图片、视频等内容转换为 `[图片]`、`[视频]`

- 特殊消息支持
    - 群聊
        - [x] @ 消息
        - [x] 回复消息（转换成@消息）
    - 频道
        - [x] @ 消息
        - [x] 回复消息（转换成@消息）
    - 未支持的消息已被替换，如： `[图片]`、 `[视频]` 等等

# 特别感谢

- [@SK-415](https://github.com/SK-415) ：感谢SK佬给予许多优秀的建议和耐心的解答。
- [@zhz-红石头](https://github.com/zhzhongshi) ：感谢红石头在代码上的帮助
- [NoneBot2](https://github.com/nonebot/nonebot2)： 插件使用的开发框架。
- [go-cqhttp](https://github.com/Mrs4s/go-cqhttp)： 稳定完善的 CQHTTP 实现。

# 二创

- [mcqq服主版](https://github.com/KarisAya/nonebot_plugin_mcqq_server) 采用本地读取log信息的方法的Minecraft Server互通消息的插件

## 贡献与支持

觉得好用可以给这个项目点个 `Star` 或者去 [爱发电](https://afdian.net/a/17TheWord) 投喂我。

有意见或者建议也欢迎提交 [Issues](https://github.com/17TheWord/nonebot-plugin-mcqq/issues)
和 [Pull requests](https://github.com/17TheWord/nonebot-plugin-mcqq/pulls)。

## 许可证

本项目使用 [GNU AGPLv3](https://choosealicense.com/licenses/agpl-3.0/) 作为开源许可证。
