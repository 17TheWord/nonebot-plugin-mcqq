package com.scareye.mcqq.event;

public class SpigotAsyncPlayerChatEvent extends SpigotMessageEvent {

    private String message;

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public SpigotAsyncPlayerChatEvent(String server_name, SpigotPlayer player, String message) {
        super(server_name, "AsyncPlayerChatEvent", "chat", player);
        this.message = message;
    }
}
