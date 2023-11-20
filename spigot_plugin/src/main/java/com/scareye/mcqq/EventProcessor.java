package com.scareye.mcqq;

import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.entity.PlayerDeathEvent;
import org.bukkit.event.player.AsyncPlayerChatEvent;
import org.bukkit.event.player.PlayerCommandPreprocessEvent;
import org.bukkit.event.player.PlayerJoinEvent;
import org.bukkit.event.player.PlayerQuitEvent;

import static com.scareye.mcqq.MC_QQ.wsClient;

import static com.scareye.mcqq.Utils.processMessageToJson;

class EventProcessor implements Listener {
    /**
     * 监听玩家聊天
     */
    @EventHandler
    void onPlayerChat(AsyncPlayerChatEvent event) {
        if (ConfigReader.getEnable() && !event.isCancelled()) {
            wsClient.sendMessage(processMessageToJson(event));
        }
    }

    /**
     * 监听玩家死亡事件
     */
    @EventHandler
    void onPlayerDeath(PlayerDeathEvent event) {
        if (ConfigReader.getDeathMessage()) {
            wsClient.sendMessage(processMessageToJson(event));
        }
    }

    /**
     * 监听玩家加入事件
     */
    @EventHandler
    void onPlayerJoin(PlayerJoinEvent event) {
        if (ConfigReader.getJoinQuit()) {
            wsClient.sendMessage(processMessageToJson(event));
        }
    }

    /**
     * 监听玩家离开事件
     */
    @EventHandler
    void onPlayerQuit(PlayerQuitEvent event) {
        if (ConfigReader.getJoinQuit()) {
            wsClient.sendMessage(processMessageToJson(event));
        }
    }

    @EventHandler
    void onPlayerCommand(PlayerCommandPreprocessEvent event) {
        if (ConfigReader.getEnable() && !event.isCancelled() && ConfigReader.getCommandMessage()) {
            wsClient.sendMessage(processMessageToJson(event));
        }
    }
}
