import re

import nonebot
import websockets
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot_plugin_guild_patch import GuildMessageEvent

from src.msg_qq_config import group_list

# 要替换的 CQ 码
cq_type = {
    "face": "表情",
    "record": "语音",
    "video": "短视频",
    "rps": "猜拳",
    "dice": "骰子",
    "anonymous": "匿名消息",
    "share": "链接分享",
    "contact": "推荐好友/群",
    "location": "位置",
    "music": "音乐",
    "image": "图片",
    "reply": "回复",
    "redbag": "红包",
    "poke": "戳一戳",
    "gift": "礼物",
    "forward": "合并转发",
    "xml": "XML",
    "json": "JSON",
    "cardimage": "大图",
}


# 连接
async def on_connect(url: str, bot):
    # 全局变量 websocket
    global websocket

    # 建立链接
    try:
        async with websockets.connect(url) as websocket:
            nonebot.logger.success("[Msq_QQ]丨已成功连接到 Msq_QQ WebSocket 服务器！")
            while True:
                # 后台日志
                # 接收消息赋值
                recv_msg = await websocket.recv()
                if group_list['group_list']:
                    for per_group in group_list['group_list']:
                        await bot.call_api("send_group_msg", group_id=per_group, message=recv_msg)
                if group_list['guild_list']:
                    for per_guild in group_list['guild_list']:
                        await bot.call_api("send_guild_channel_msg", guild_id=per_guild['guild_id'],
                                           channel_id=per_guild['channel_id'], message=recv_msg)
                nonebot.logger.success("[Msg_QQ]丨发送消息：" + recv_msg)
    except (OSError, websockets.exceptions.ConnectionClosedError, websockets.exceptions.ConnectionClosedOK) as e:
        nonebot.logger.error("[Msq_QQ]：无法连接到 WebSocket 服务器，正在重新连接。")
        await on_connect(url=url, bot=bot)


# todo 17 改成 MessageSegment 格式解析
async def send_msg_to_mc(event, bot):
    get_msg = str(event.raw_message).replace("\r\n", " ")  # 源消息

    # 匹配 @ CQ 码
    # 匹配 回复 信息
    if "[CQ:reply,id=" in get_msg:
        # 提取被回复的消息ID
        message_id = re.findall(r"\[CQ:reply,id=(.+?)]", get_msg)
        # 替换 回复 CQ码
        get_msg = get_msg.replace(f"[CQ:reply,id={message_id[0]}]", "回复 ")

        # 替换 回复 中的 @ CQ码
        if "[CQ:at,qq=" in get_msg:
            cq_qq_list = re.findall(r"\[CQ:at,qq=(.+?)]", get_msg)

            for per_user_id in cq_qq_list:
                get_msg = get_msg.replace(f"[CQ:at,qq={per_user_id}]", "@" + await get_member_nickname(
                    bot=bot, event=event, user_id=per_user_id
                )
                                          )

    # 匹配 @ 信息
    elif "[CQ:at,qq=" in get_msg:
        cq_qq_list = re.findall(r"\[CQ:at,qq=(.+?)]", get_msg)

        for per_user_id in cq_qq_list:
            get_msg = get_msg.replace(f"[CQ:at,qq={per_user_id}]", "@" + await get_member_nickname(
                bot=bot, event=event,
                user_id=per_user_id
            )
                                      )
    # 其他消息
    for i in event.message:
        print(i.text)
    # 拼接信息类型
    final_msg = re.sub(r'\[CQ.*]', "", get_msg)
    msg_type_list = re.findall(r'CQ:(.+?),', get_msg)

    temp_str = ""
    for msg_type in msg_type_list:
        if msg_type in cq_type:
            temp_str += f"[{cq_type[msg_type]}]"
    final_msg += temp_str
    # 发送消息和日志
    await websocket.send(f"{event.sender.nickname} 说：{final_msg}")
    nonebot.logger.success(f"[Msq_QQ]丨发送到 MC 服务器：{event.sender.nickname} 说：{final_msg}")


# 获取群成员昵称
async def get_member_nickname(bot, event, user_id):
    # 判断从 群 或者 频道 获取成员信息
    if isinstance(event, GroupMessageEvent):
        member_info = await bot.get_group_member_info(group_id=event.group_id, user_id=user_id)
    elif isinstance(event, GuildMessageEvent):
        await bot.get_guild_member_profile(guild_id=event.guild_id, user_id=str(user_id))
    # 返回成员昵称
    return member_info['nickname']
