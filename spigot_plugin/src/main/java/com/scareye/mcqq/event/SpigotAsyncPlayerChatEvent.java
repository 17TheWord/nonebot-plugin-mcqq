package com.scareye.mcqq.event;

public class SpigotAsyncPlayerChatEvent extends SpigotMessageEvent {

    public SpigotAsyncPlayerChatEvent(String server_name, SpigotPlayer player, String message) {
        super(server_name, "AsyncPlayerChatEvent", "chat", player, message);
    }
}
