package com.scareye.mcqq;

import com.alibaba.fastjson.JSONObject;

import net.md_5.bungee.api.ChatColor;
import net.md_5.bungee.api.chat.BaseComponent;
import net.md_5.bungee.api.chat.ClickEvent;
import net.md_5.bungee.api.chat.HoverEvent;
import net.md_5.bungee.api.chat.TextComponent;
import net.md_5.bungee.api.chat.hover.content.Text;

import org.bukkit.Bukkit;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.player.AsyncPlayerChatEvent;
import org.bukkit.event.player.PlayerJoinEvent;
import org.bukkit.event.player.PlayerQuitEvent;
import org.bukkit.event.entity.PlayerDeathEvent;

import java.util.Collection;

import static com.scareye.mcqq.MC_QQ.*;

class EventProcessor implements Listener {
    /**
     * 消息的处理
     * @return
     */
    static BaseComponent onJsonMessage(String message) {
        JSONObject msgJson = JSONObject.parseObject(message);
        // 组合消息
        TextComponent component = new TextComponent("[MC_QQ] ");
        component.setColor(ChatColor.YELLOW);

        TextComponent senderName = new TextComponent(msgJson.getString("senderName"));
        senderName.setColor(ChatColor.AQUA);
        component.addExtra(senderName);

        TextComponent sayWay = new TextComponent(ConfigReader.getSayWay());
        sayWay.setColor(ChatColor.WHITE);
        component.addExtra(sayWay);
        StringBuilder msgText = new StringBuilder("[MC_QQ]丨" + msgJson.getString("senderName") + ConfigReader.getSayWay());
        for (Object jsonArray : msgJson.getJSONArray("message")) {
            String msgType = JSONObject.parseObject(String.valueOf(jsonArray)).getString("msgType");
            String msgData = JSONObject.parseObject(String.valueOf(jsonArray)).getString("msgData");

            if (msgData.equals("/list")) {
                Collection<? extends Player> onlinePlayerList = Bukkit.getServer().getOnlinePlayers();
                StringBuilder playerList = new StringBuilder();
                if (onlinePlayerList.isEmpty()) {
                    playerList = new StringBuilder("当前没有玩家在线");
                } else {
                    for (Player player : onlinePlayerList) {
                        playerList.append(player.getName()).append("\n");
                    }
                }
                websocket.sendMessage(playerList.toString());
            } else {
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
                        msgComponent.setText(msgData + " ");
                        msgComponent.setColor(ChatColor.GREEN);
                        break;
                    default:
                        msgComponent.setText("[" + msgType + "] ");
                        msgComponent.setColor(ChatColor.WHITE);
                        break;
                }
                msgText.append(msgData);
                component.addExtra(msgComponent);
                instance.getServer().spigot().broadcast(component);
                say(String.valueOf(msgText));
            }
        }
        return component;
    }


    /**
     * 监听玩家聊天
     */
    @EventHandler
    void onPlayerChat(AsyncPlayerChatEvent event) {
        if (!event.isCancelled()) {
            websocket.sendMessage(event.getPlayer().getName() + ConfigReader.getSayWay() + event.getMessage());
        }
    }

    /**
     * 监听玩家死亡事件
     */
    @EventHandler
    void onPlayerDeath(PlayerDeathEvent event) {
        if (ConfigReader.getDeathMessage()) {
            websocket.sendMessage(event.getDeathMessage());
        }
    }

    /**
     * 监听玩家加入事件
     */
    @EventHandler
    void onPlayerJoin(PlayerJoinEvent event) {
        if (ConfigReader.getJoinQuit()) {
            websocket.sendMessage(event.getPlayer().getName() + " 加入了服务器");
        }
    }

    /**
     * 监听玩家离开事件
     */
    @EventHandler
    void onPlayerQuit(PlayerQuitEvent event) {
        if (ConfigReader.getJoinQuit()) {
            websocket.sendMessage(event.getPlayer().getName() + " 离开了服务器");
        }
    }
}
