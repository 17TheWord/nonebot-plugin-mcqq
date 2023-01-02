# 前言

## 介绍

- 基于 `NoneBot` 的与 `Minecraft Server` 互通消息插件

- 支持QQ群、QQ频道

- 项目地址：[17TheWord/nonebot-plugin-mcqq](https://github.com/17TheWord/nonebot-plugin-mcqq)

---

# 功能

- 推送消息列表
  - 服务器 -> QQ
    - [x] 加入 / 离开 服务器消息
    - [x] 玩家聊天信息
    - [x] 玩家死亡信息（死亡信息为英文，计划使用翻译解决。`MOD` 服务端不适用。）
  - QQ -> 服务器
    - [x] 指令（`Rcon` 版）
    - [x] 群员聊天文本
    - [x] 图片、视频等内容转换为 `[图片]`、`[视频]`

- 特殊消息支持
  - 群聊
    - [x] @ 消息
    - [ ] 回复消息
  - 频道
    - [x] @ 消息
    - [ ] 回复消息
  - 未支持的消息已被替换，如： `[图片]`、 `[视频]` 等等

---

## 特别感谢
- [@SK-415](https://github.com/SK-415) ：感谢SK佬给予许多优秀的建议和耐心的解答。
- [@zhz-红石头](https://github.com/zhzhongshi) ：感谢红石头在代码上的帮助
- [NoneBot2](https://github.com/nonebot/nonebot2)： 插件使用的开发框架。
- [go-cqhttp](https://github.com/Mrs4s/go-cqhttp)： 稳定完善的 CQHTTP 实现。
