package com.scareye.mcqq.event;

public class SpigotMessageEvent extends SpigotEvent {

    private SpigotPlayer player;

    public SpigotPlayer getPlayer() {
        return player;
    }

    public void setPlayer(SpigotPlayer player) {
        this.player = player;
    }

    public SpigotMessageEvent(String server_name, String event_name, String sub_type, SpigotPlayer player) {
        super(server_name, event_name, "message", sub_type);
        this.player = player;
    }
}
