package com.scareye.mcqq.event;

public class SpigotNoticeEvent extends SpigotEvent {

    private SpigotPlayer player;

    public SpigotPlayer getPlayer() {
        return player;
    }

    public void setPlayer(SpigotPlayer player) {
        this.player = player;
    }

    public SpigotNoticeEvent(String server_name, String event_name, String sub_type, SpigotPlayer player) {
        super(server_name, event_name, "notice", sub_type);
        this.player = player;
    }
}
