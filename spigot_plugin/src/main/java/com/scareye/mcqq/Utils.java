package com.scareye.mcqq;

import com.google.gson.Gson;
import com.scareye.mcqq.event.*;
import com.scareye.mcqq.returnBody.MinecraftReturnBody;
import com.scareye.mcqq.returnBody.MsgItem;
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
import org.bukkit.event.player.PlayerCommandPreprocessEvent;
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
        // 组合消息
        TextComponent component = new TextComponent("[MC_QQ] ");
        component.setColor(ChatColor.YELLOW);
        StringBuilder msgLogText = new StringBuilder();

        Gson gson = new Gson();
        MinecraftReturnBody minecraftReturnBody = gson.fromJson(message, MinecraftReturnBody.class);
        System.out.println(minecraftReturnBody.toString());

        for (MsgItem msgItem : minecraftReturnBody.getMessage()) {
            TextComponent msgComponent = new TextComponent();
            msgComponent.setText(msgItem.getMsgText());
            msgComponent.setColor(getColor(msgItem.getColor()));
            if (msgItem.getActionEvent() != null) {
                msgComponent.setClickEvent(new ClickEvent(ClickEvent.Action.OPEN_URL, msgItem.getActionEvent().getClickEventUrl()));
                msgComponent.setHoverEvent(new HoverEvent(HoverEvent.Action.SHOW_TEXT, new Text(msgItem.getActionEvent().getHoverEventText())));
            }
            component.addExtra(msgComponent);
            msgLogText.append(msgItem.getMsgText());
        }
        say(msgLogText.toString());
        return component;
    }


    /**
     * @param color 颜色
     * @return ChatColor 对象
     */
    static ChatColor getColor(String color) {
        switch (color) {
            case "black":
                return ChatColor.BLACK;
            case "dark_blue":
                return ChatColor.DARK_BLUE;
            case "dark_green":
                return ChatColor.DARK_GREEN;
            case "dark_aqua":
                return ChatColor.DARK_AQUA;
            case "dark_red":
                return ChatColor.DARK_RED;
            case "dark_purple":
                return ChatColor.DARK_PURPLE;
            case "gold":
                return ChatColor.GOLD;
            case "gray":
                return ChatColor.GRAY;
            case "dark_gray":
                return ChatColor.DARK_GRAY;
            case "blue":
                return ChatColor.BLUE;
            case "green":
                return ChatColor.GREEN;
            case "aqua":
                return ChatColor.AQUA;
            case "red":
                return ChatColor.RED;
            case "light_purple":
                return ChatColor.LIGHT_PURPLE;
            case "yellow":
                return ChatColor.YELLOW;
            case "white":
            default:
                return ChatColor.WHITE;
        }

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
        } else if (event instanceof PlayerCommandPreprocessEvent) {
            SpigotPlayerCommandPreprocessEvent spigotPlayerCommandPreprocessEvent = new SpigotPlayerCommandPreprocessEvent(
                    server_name,
                    getSpigotPlayer(((PlayerCommandPreprocessEvent) event).getPlayer()),
                    ((PlayerCommandPreprocessEvent) event).getMessage()
            );
            jsonData = gson.toJson(spigotPlayerCommandPreprocessEvent);
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
