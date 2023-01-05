package com.scareye.mcqq;

import com.alibaba.fastjson.JSONObject;
import net.md_5.bungee.api.ChatColor;

import net.md_5.bungee.api.chat.ClickEvent;
import net.md_5.bungee.api.chat.HoverEvent;
import net.md_5.bungee.api.chat.TextComponent;
import net.md_5.bungee.api.chat.hover.content.Text;
import org.bukkit.Bukkit;
import org.bukkit.command.CommandSender;
import org.bukkit.entity.Player;
import org.bukkit.event.Event;
import org.bukkit.event.entity.PlayerDeathEvent;
import org.bukkit.event.player.AsyncPlayerChatEvent;
import org.bukkit.event.player.PlayerJoinEvent;
import org.bukkit.event.player.PlayerQuitEvent;

import java.util.Objects;


public class Utils {

    /**
     * 定义方法 Say()
     * 向服务器后台发送信息
     */
    static void say(String msg) {
        CommandSender sender = Bukkit.getConsoleSender();
        sender.sendMessage("[MC_QQ] " + msg);
    }

    /**
     * 来自 NoneBot 的 JSON 消息的处理
     */
    static TextComponent processJsonMessage(String message) {
        JSONObject msgJson = JSONObject.parseObject(message);
        // 组合消息
        TextComponent component = new TextComponent("[MC_QQ] ");
        component.setColor(ChatColor.YELLOW);
        StringBuilder msgText = new StringBuilder();

        // 判断是否启用群聊名称前缀
        if (ConfigReader.getDisplayGroupName()) {
            // 获取 信息类型
            JSONObject messageType = msgJson.getJSONObject("message_type");
            TextComponent messageFrom = new TextComponent();
            switch (messageType.getString("type")) {
                case "group":
                    messageFrom.setText(messageType.getString("group_name") + " ");
                    msgText.append(messageType.getString("group_name")).append(" ");
                    break;
                case "guild":
                    messageFrom.setText(messageType.getString("guild_name") + "丨" + messageType.getString("channel_name") + " ");
                    msgText.append(messageType.getString("guild_name")).append("丨").append(messageType.getString("channel_name")).append(" ");
                    break;
            }
            messageFrom.setColor(ChatColor.GOLD);
            component.addExtra(messageFrom);
        }

        // 发送人信息
        TextComponent senderName = new TextComponent(msgJson.getString("senderName"));
        senderName.setColor(ChatColor.AQUA);
        // 将 发送者 添加至 组合消息
        component.addExtra(senderName);
        // 将 发送者 添加至 msgText
        msgText.append(msgJson.getString("senderName")).append(ConfigReader.getSayWay());

        TextComponent sayWay = new TextComponent(ConfigReader.getSayWay());
        sayWay.setColor(ChatColor.WHITE);
        component.addExtra(sayWay);
        for (Object jsonArray : msgJson.getJSONArray("message")) {
            String msgType = JSONObject.parseObject(String.valueOf(jsonArray)).getString("msgType");
            String msgData = JSONObject.parseObject(String.valueOf(jsonArray)).getString("msgData");

            TextComponent msgComponent = new TextComponent();
            switch (msgType) {
                case "text":
                    msgComponent.setText(msgData + " ");
                    msgComponent.setColor(ChatColor.WHITE);
                    break;
                case "face":
                    msgComponent.setText("[表情] ");
                    msgComponent.setColor(ChatColor.GOLD);
                    break;
                case "record":
                    msgComponent.setText("[语音] ");
                    msgComponent.setColor(ChatColor.LIGHT_PURPLE);
                    break;
                case "video":
                    msgComponent.setText("[视频] ");
                    msgComponent.setColor(ChatColor.LIGHT_PURPLE);
                    msgComponent.setClickEvent(new ClickEvent(ClickEvent.Action.OPEN_URL, msgData));
                    msgComponent.setHoverEvent(new HoverEvent(HoverEvent.Action.SHOW_TEXT, new Text("查看视频")));
                    break;
                case "rps":
                    msgComponent.setText("[猜拳] ");
                    msgComponent.setColor(ChatColor.WHITE);
                    break;
                case "dice":
                    msgComponent.setText("[骰子] ");
                    msgComponent.setColor(ChatColor.WHITE);
                    break;
                case "anonymous":
                    msgComponent.setText("[匿名消息] ");
                    msgComponent.setColor(ChatColor.WHITE);
                    break;
                case "share":
                    msgComponent.setText("[分享] ");
                    msgComponent.setColor(ChatColor.WHITE);
                    break;
                case "contact":
                    msgComponent.setText("[推荐] ");
                    msgComponent.setColor(ChatColor.WHITE);
                    break;
                case "location":
                    msgComponent.setText("[位置] ");
                    msgComponent.setColor(ChatColor.WHITE);
                case "music":
                    msgComponent.setText("[音乐] ");
                    msgComponent.setColor(ChatColor.YELLOW);
                    msgComponent.setClickEvent(new ClickEvent(ClickEvent.Action.OPEN_URL, msgData));
                    msgComponent.setHoverEvent(new HoverEvent(HoverEvent.Action.SHOW_TEXT, new Text("查看音乐")));
                    break;
                case "image":
                    msgComponent.setText("[图片] ");
                    msgComponent.setColor(ChatColor.AQUA);
                    msgComponent.setClickEvent(new ClickEvent(ClickEvent.Action.OPEN_URL, msgData));
                    msgComponent.setHoverEvent(new HoverEvent(HoverEvent.Action.SHOW_TEXT, new Text("查看图片")));
                    break;
                case "redbag":
                    msgComponent.setText("[红包] ");
                    msgComponent.setColor(ChatColor.RED);
                    break;
                case "poke":
                    msgComponent.setText("[戳一戳] ");
                    msgComponent.setColor(ChatColor.GOLD);
                    break;
                case "gift":
                    msgComponent.setText("[礼物] ");
                    msgComponent.setColor(ChatColor.YELLOW);
                    break;
                case "forward":
                    msgComponent.setText("[合并转发] ");
                    msgComponent.setColor(ChatColor.WHITE);
                    break;
                case "at":
                    msgComponent.setText(msgData.replace(" ", "") + " ");
                    msgComponent.setColor(ChatColor.GREEN);
                    break;
                default:
                    msgComponent.setText("[" + msgType + "] ");
                    msgComponent.setColor(ChatColor.WHITE);
                    break;
            }
            msgText.append(msgData);
            component.addExtra(msgComponent);

        }
        // 后台打印文本
        say(String.valueOf(msgText));
        return component;
    }

    /**
     * @param event 事件
     * @return 事件的 Json对象
     */
    static String processMessageToJson(Event event) {
        JSONObject jsonMessage = new JSONObject();
        jsonMessage.put("server_name", ConfigReader.getServerName());
        jsonMessage.put("event_name", event.getEventName());

        if (event instanceof AsyncPlayerChatEvent) {
            /*
             将玩家信息添加至 Json 对象中
             将 聊天 消息添加至 Json 对象中
             */
            jsonMessage.put("player", getPlayerJson(((AsyncPlayerChatEvent) event).getPlayer()));
            jsonMessage.put("message", getMessageJson("text", ((AsyncPlayerChatEvent) event).getPlayer().getName() + ConfigReader.getSayWay() + ((AsyncPlayerChatEvent) event).getMessage()));

        } else if (event instanceof PlayerJoinEvent) {
            /*
             将玩家信息添加至 Json 对象中
             将 加入 消息添加至 Json 对象中
             */
            jsonMessage.put("player", getPlayerJson(((PlayerJoinEvent) event).getPlayer()));
            jsonMessage.put("message", getMessageJson("text", ((PlayerJoinEvent) event).getPlayer().getName() + " 加入了服务器"));

        } else if (event instanceof PlayerQuitEvent) {
            /*
             将玩家信息添加至 Json 对象中
             将 离开 消息添加至 Json 对象中
             */
            jsonMessage.put("player", getPlayerJson(((PlayerQuitEvent) event).getPlayer()));
            jsonMessage.put("message", getMessageJson("text", ((PlayerQuitEvent) event).getPlayer().getName() + " 离开了服务器"));
        } else if (event instanceof PlayerDeathEvent) {
            /*
             将玩家信息添加至 Json 对象中
             将 死亡 消息添加至 Json 对象中
             */
            jsonMessage.put("player", getPlayerJson(((PlayerDeathEvent) event).getEntity()));
            jsonMessage.put("message", getMessageJson("text", ((PlayerDeathEvent) event).getDeathMessage()));
        }

        return jsonMessage.toJSONString();
    }

    /**
     * @param player 玩家
     * @return 玩家 Json对象
     */
    static JSONObject getPlayerJson(Player player) {
        // 玩家 Json
        JSONObject playerObject = new JSONObject();

        // UUID
        playerObject.put("uuid", player.getUniqueId());

        // 得到一个Address对象,包括这个玩家的IP以及登入端口
        playerObject.put("address", player.getAddress());
        // 判断玩家是否能飞起来
        playerObject.put("allow_flight", player.getAllowFlight());
        // 获得玩家在聊天信息中的昵称
        playerObject.put("display_name", player.getDisplayName());
        // 经验进度百分比
        playerObject.put("exp", player.getExp());
        // 得到该玩家飞行速度
        playerObject.put("fly_speed", player.getFlySpeed());

        // 获取客户端显示的血量的"压缩率"
        playerObject.put("health_scale", player.getHealthScale());
        // 得到玩家的等级
        playerObject.put("level", player.getLevel());
        // 返回玩家本地语言环境
        playerObject.put("locale", player.getLocale());
        // 返回该玩家的玩家名
        playerObject.put("nickname", player.getName());
        // Ping
        playerObject.put("ping", player.getPing());

        // 得到玩家显示在tab列表中的名称
        playerObject.put("player_list_name", player.getPlayerListName());
        // 得到玩家的客户端的当前时间,单位为tick
        playerObject.put("player_time", player.getPlayerTime());
        // 返回玩家的客户端的当前时间与玩家当前世界时间的差值
        playerObject.put("player_time_offset", player.getPlayerTimeOffset());
        // 得到玩家总共获得了多少经验(等级和经验)
        playerObject.put("total_exp", player.getTotalExperience());
        // 得到行走速度
        playerObject.put("walk_speed", player.getWalkSpeed());

        // 是否飞行
        playerObject.put("is_flying", player.isFlying());
        // 血量是否被 “压缩”
        playerObject.put("is_health_scaled", player.isHealthScaled());
        // 如果玩家时间于当前世界时间保持了一定的差值则返回true
        playerObject.put("is_player_time_relative", player.isPlayerTimeRelative());
        // 判断玩家是否在潜行中
        playerObject.put("is_sneaking", player.isSneaking());
        // 判断玩家是否在疾跑
        playerObject.put("is_sprinting", player.isSprinting());
        return playerObject;
    }

    /**
     * @param type 类型
     * @param data 内容
     * @return 消息 Json对象
     */
    static JSONObject getMessageJson(String type, String data) {
        JSONObject messageJson = new JSONObject();
        messageJson.put("type", type);
        messageJson.put("data", data);
        return messageJson;
    }

}
