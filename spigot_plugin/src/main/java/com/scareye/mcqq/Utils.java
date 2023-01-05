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
        StringBuilder msgLogText = new StringBuilder();

        // 判断是否启用群聊名称前缀
        if (ConfigReader.getDisplayGroupName()) {
            // 获取 信息类型
            JSONObject messageType = msgJson.getJSONObject("message_type");
            TextComponent messageFrom = new TextComponent();
            switch (messageType.getString("type")) {
                case "group":
                    messageFrom.setText(messageType.getString("group_name") + " ");
                    msgLogText.append(messageType.getString("group_name")).append(" ");
                    break;
                case "guild":
                    messageFrom.setText(messageType.getString("guild_name") + "丨" + messageType.getString("channel_name") + " ");
                    msgLogText.append(messageType.getString("guild_name")).append("丨").append(messageType.getString("channel_name")).append(" ");
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
        // 将 发送者 添加至 msgLogText
        msgLogText.append(msgJson.getString("senderName")).append(ConfigReader.getSayWay());

        TextComponent sayWay = new TextComponent(ConfigReader.getSayWay());
        sayWay.setColor(ChatColor.WHITE);
        component.addExtra(sayWay);
        for (Object jsonArray : msgJson.getJSONArray("message")) {
            String msgType = JSONObject.parseObject(String.valueOf(jsonArray)).getString("msgType");
            String msgData = JSONObject.parseObject(String.valueOf(jsonArray)).getString("msgData");

            TextComponent msgComponent = new TextComponent();
            String textContent;
            ChatColor color;
            switch (msgType) {
                case "text":
                    textContent = msgData;
                    color = ChatColor.WHITE;
                    break;
                case "face":
                    textContent = "[表情]";
                    color = ChatColor.GOLD;
                    break;
                case "record":
                    textContent = "[语音]";
                    color = ChatColor.LIGHT_PURPLE;
                    break;
                case "video":
                    textContent = "[视频]";
                    color = ChatColor.LIGHT_PURPLE;
                    msgComponent.setClickEvent(new ClickEvent(ClickEvent.Action.OPEN_URL, msgData));
                    msgComponent.setHoverEvent(new HoverEvent(HoverEvent.Action.SHOW_TEXT, new Text("查看视频")));
                    break;
                case "rps":
                    textContent = "[猜拳]";
                    color = ChatColor.WHITE;
                    break;
                case "dice":
                    textContent = "[骰子]";
                    color = ChatColor.WHITE;
                    break;
                case "anonymous":
                    textContent = "[匿名消息]";
                    color = ChatColor.WHITE;
                    break;
                case "share":
                    textContent = "[分享]";
                    color = ChatColor.WHITE;
                    break;
                case "contact":
                    textContent = "[推荐]";
                    color = ChatColor.WHITE;
                    break;
                case "location":
                    textContent = "[位置]";
                    color = ChatColor.WHITE;
                    break;
                case "music":
                    textContent = "[音乐]";
                    color = ChatColor.YELLOW;
                    msgComponent.setClickEvent(new ClickEvent(ClickEvent.Action.OPEN_URL, msgData));
                    msgComponent.setHoverEvent(new HoverEvent(HoverEvent.Action.SHOW_TEXT, new Text("查看音乐")));
                    break;
                case "image":
                    textContent = "[图片]";
                    color = ChatColor.AQUA;
                    msgComponent.setClickEvent(new ClickEvent(ClickEvent.Action.OPEN_URL, msgData));
                    msgComponent.setHoverEvent(new HoverEvent(HoverEvent.Action.SHOW_TEXT, new Text("查看图片")));
                    break;
                case "redbag":
                    textContent = "[红包]";
                    color = ChatColor.RED;
                    break;
                case "poke":
                    textContent = "[戳一戳]";
                    color = ChatColor.GOLD;
                    break;
                case "gift":
                    textContent = "[礼物]";
                    color = ChatColor.YELLOW;
                    break;
                case "forward":
                    textContent = "[合并转发]";
                    color = ChatColor.WHITE;
                    break;
                case "at":
                    textContent = msgData.replace(" ", "");
                    color = ChatColor.GREEN;
                    break;
                default:
                    textContent = "[" + msgType + "]";
                    color = ChatColor.WHITE;
                    break;
            }
            textContent += " ";
            // 为消息设置 文本
            msgComponent.setText(textContent);
            // 为消息设置 颜色
            msgComponent.setColor(color);
            // 将消息装入 日志文本队列
            msgLogText.append(textContent);
            // 将消息装入 消息队列
            component.addExtra(msgComponent);

        }
        // 后台打印文本
        say(String.valueOf(msgLogText));
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
