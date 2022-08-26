# nonebot-plugin-mcqq

基于 `NoneBot` 的与 `Minecraft Server` 互通消息插件

支持QQ群、QQ频道

# 文档

- [正在不断更新的文档](https://doc.scareye.com/mc_qq/)

# 功能

- 即将更新
  - 适用于原版服务端的 `MCRCON` + `WebSockets` 分支版本
  - 理论上同样适用于纯 `MOD` 端
  - 缺陷为 Server 发送到 Bot 的第一条消息会失败，后续消息正常
  - `[图片]`、`[视频]` 等特殊消息可通过点击在浏览器查看

- 推送消息列表
  - 服务器 -> QQ
    - 加入 / 离开 服务器消息
    - 玩家聊天信息
  - QQ -> 服务器
    - 群员聊天文本
    - 图片、视频等内容转换为 `[图片]`、`[视频]`
  - 计划
    - 将图片、视频等消息更改为可单击通过浏览器打开

- 特殊消息支持
  - 群聊
    - [x] @ 消息
    - [x] 回复消息
  - 频道
    - [ ] @ 消息
    - [ ] 回复消息
  - 未支持的消息已被替换，如： `[图片]`、 `[视频]` 等等

# 特别感谢
- [@SK-415](https://github.com/SK-415) ：感谢SK佬给予许多优秀的建议和耐心的解答。
- [@zhz-红石头](https://github.com/zhzhongshi) ：感谢红石头在代码上的帮助
- [NoneBot2](https://github.com/nonebot/nonebot2)： 插件使用的开发框架。
- [go-cqhttp](https://github.com/Mrs4s/go-cqhttp)： 稳定完善的 CQHTTP 实现。
