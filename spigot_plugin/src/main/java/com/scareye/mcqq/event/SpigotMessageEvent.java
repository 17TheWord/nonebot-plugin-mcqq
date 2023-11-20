package com.scareye.mcqq.event;

public class SpigotMessageEvent extends SpigotEvent {

    private SpigotPlayer player;

    private String message;

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public SpigotPlayer getPlayer() {
        return player;
    }

    public void setPlayer(SpigotPlayer player) {
        this.player = player;
    }

    public SpigotMessageEvent(String server_name, String event_name, String sub_type, SpigotPlayer player, String message) {
        super(server_name, event_name, "message", sub_type);
        this.message = message;
        this.player = player;
    }
}
