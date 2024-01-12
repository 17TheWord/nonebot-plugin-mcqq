package com.github.theword.event;

public class MinecraftPlayerChatEvent extends MinecraftMessageEvent {
    public MinecraftPlayerChatEvent(String messageId, MinecraftPlayer player, String message) {
        super("MinecraftPlayerChatEvent", "chat", messageId, player, message);
    }
}
