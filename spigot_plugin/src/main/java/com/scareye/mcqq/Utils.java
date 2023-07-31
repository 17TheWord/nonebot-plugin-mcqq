package com.scareye.mcqq;

import com.google.gson.Gson;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.scareye.mcqq.event.*;
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

        JsonObject jsonObject = JsonParser.parseString(message).getAsJsonObject();
        // 组合消息
        TextComponent component = new TextComponent("[MC_QQ] ");
        component.setColor(ChatColor.YELLOW);
        StringBuilder msgLogText = new StringBuilder();

        for (JsonElement element : jsonObject.get("message").getAsJsonArray()) {
            JsonObject msgJson = element.getAsJsonObject();

            String msgType = msgJson.get("msgType").getAsString();
            String msgData = msgJson.get("msgData").getAsString();

            TextComponent msgComponent = new TextComponent();
            String textContent;
            ChatColor color;
            switch (msgType) {
                case "group_name" -> {
                    textContent = msgData;
                    color = ChatColor.GOLD;
                }
                case "senderName" -> {
                    textContent = msgData;
                    color = ChatColor.AQUA;
                }
                case "text" -> {
                    textContent = msgData;
                    color = ChatColor.WHITE;
                }
                case "face" -> {
                    textContent = "[表情]";
                    color = ChatColor.GOLD;
                }
                case "record" -> {
                    textContent = "[语音]";
                    color = ChatColor.LIGHT_PURPLE;
                }
                case "video" -> {
                    textContent = "[视频]";
                    color = ChatColor.LIGHT_PURPLE;
                    msgComponent.setClickEvent(new ClickEvent(ClickEvent.Action.OPEN_URL, msgData));
                    msgComponent.setHoverEvent(new HoverEvent(HoverEvent.Action.SHOW_TEXT, new Text("查看视频")));
                }
                case "rps" -> {
                    textContent = "[猜拳]";
                    color = ChatColor.WHITE;
                }
                case "dice" -> {
                    textContent = "[骰子]";
                    color = ChatColor.WHITE;
                }
                case "anonymous" -> {
                    textContent = "[匿名消息]";
                    color = ChatColor.WHITE;
                }
                case "share" -> {
                    textContent = "[分享]";
                    color = ChatColor.WHITE;
                }
                case "contact" -> {
                    textContent = "[推荐]";
                    color = ChatColor.WHITE;
                }
                case "location" -> {
                    textContent = "[位置]";
                    color = ChatColor.WHITE;
                }
                case "music" -> {
                    textContent = "[音乐]";
                    color = ChatColor.YELLOW;
                    msgComponent.setClickEvent(new ClickEvent(ClickEvent.Action.OPEN_URL, msgData));
                    msgComponent.setHoverEvent(new HoverEvent(HoverEvent.Action.SHOW_TEXT, new Text("查看音乐")));
                }
                case "image" -> {
                    textContent = "[图片]";
                    color = ChatColor.AQUA;
                    msgComponent.setClickEvent(new ClickEvent(ClickEvent.Action.OPEN_URL, msgData));
                    msgComponent.setHoverEvent(new HoverEvent(HoverEvent.Action.SHOW_TEXT, new Text("查看图片")));
                }
                case "redbag" -> {
                    textContent = "[红包]";
                    color = ChatColor.RED;
                }
                case "poke" -> {
                    textContent = "[戳一戳]";
                    color = ChatColor.GOLD;
                }
                case "gift" -> {
                    textContent = "[礼物]";
                    color = ChatColor.YELLOW;
                }
                case "forward" -> {
                    textContent = "[合并转发]";
                    color = ChatColor.WHITE;
                }
                case "at" -> {
                    textContent = msgData.replace(" ", "");
                    color = ChatColor.GREEN;
                }
                default -> {
                    textContent = "[" + msgType + "]";
                    color = ChatColor.WHITE;
                }
            }
//            textContent += " ";
            // 为消息设置 文本
            msgComponent.setText(textContent);
            // 为消息设置 颜色
            msgComponent.setColor(color);

            // 将消息装入 日志文本队列
            msgLogText.append(textContent);
            // 将消息装入 消息队列
            component.addExtra(msgComponent);

            if (msgType.equals("senderName")) {
                // 说话方式
                TextComponent sayWay = new TextComponent(ConfigReader.getSayWay());
                sayWay.setColor(ChatColor.WHITE);
                component.addExtra(sayWay);
                // 说话方式装入 日志文本队列
                msgLogText.append(ConfigReader.getSayWay());
            }

        }
        // 后台打印文本
        say(String.valueOf(msgLogText));
        return component;
    }

    /**
     * @param event 事件
     * @return 事件的 Json 字符串
     */
    static String processMessageToJson(Event event) {
        Gson gson = new Gson();

        String server_name = ConfigReader.getServerName();
        String jsonData;

        if (event instanceof AsyncPlayerChatEvent) {
            SpigotAsyncPlayerChatEvent spigotAsyncPlayerChatEvent = new SpigotAsyncPlayerChatEvent(
                    server_name,
                    getSpigotPlayer(((AsyncPlayerChatEvent) event).getPlayer()),
                    ((AsyncPlayerChatEvent) event).getMessage()
            );
            jsonData = gson.toJson(spigotAsyncPlayerChatEvent);
        } else if (event instanceof PlayerJoinEvent) {
            SpigotPlayerJoinEvent spigotPlayerJoinEvent = new SpigotPlayerJoinEvent(
                    server_name,
                    getSpigotPlayer(((PlayerJoinEvent) event).getPlayer())
            );
            jsonData = gson.toJson(spigotPlayerJoinEvent);
        } else if (event instanceof PlayerQuitEvent) {
            SpigotPlayerQuitEvent spigotPlayerQuitEvent = new SpigotPlayerQuitEvent(
                    server_name,
                    getSpigotPlayer(((PlayerQuitEvent) event).getPlayer())
            );
            jsonData = gson.toJson(spigotPlayerQuitEvent);
        } else if (event instanceof PlayerDeathEvent) {
            SpigotPlayerDeathEvent spigotPlayerDeathEvent = new SpigotPlayerDeathEvent(
                    server_name,
                    getSpigotPlayer(((PlayerDeathEvent) event).getEntity()),
                    ((PlayerDeathEvent) event).getDeathMessage()
            );
            jsonData = gson.toJson(spigotPlayerDeathEvent);
        } else {
            say("未知事件: " + event.getEventName());
            jsonData = gson.toJson(event);
        }
        return jsonData;
    }

    /**
     * @param player 玩家
     * @return SpigotPlayer 对象
     */
    static SpigotPlayer getSpigotPlayer(Player player) {
        return new SpigotPlayer(
                player.getUniqueId().toString(),
                player.getName(),
                player.getDisplayName(),
                player.getDisplayName(),
                Objects.requireNonNull(player.getAddress()).toString(),
                player.isHealthScaled(),
                player.getHealthScale(),
                player.getExp(),
                player.getTotalExperience(),
                player.getLevel(),
                player.getLocale(),
                player.getPing(),
                player.getPlayerTime(),
                player.isPlayerTimeRelative(),
                player.getPlayerTimeOffset(),
                player.getWalkSpeed(),
                player.getFlySpeed(),
                player.getAllowFlight(),
                player.isSprinting(),
                player.isSneaking(),
                player.isFlying(),
                player.isOp()
        );
    }

    /**
     * 字符串转为 unicode 编码
     *
     * @param string 字符串
     * @return unicode编码
     */
    static String unicodeEncode(String string) {
        char[] utfBytes = string.toCharArray();
        StringBuilder unicodeBytes = new StringBuilder();
        for (char utfByte : utfBytes) {
            String hexB = Integer.toHexString(utfByte);
            if (hexB.length() <= 2) {
                hexB = "00" + hexB;
            }
            unicodeBytes.append("\\u").append(hexB);
        }
        return unicodeBytes.toString();
    }
}
