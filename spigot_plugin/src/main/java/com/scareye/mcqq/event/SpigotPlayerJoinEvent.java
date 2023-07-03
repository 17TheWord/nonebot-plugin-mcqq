package com.scareye.mcqq.event;

public class SpigotPlayerJoinEvent extends SpigotNoticeEvent {


    public SpigotPlayerJoinEvent(String server_name, SpigotPlayer player) {
        super(server_name, "PlayerJoinEvent", "join", player);
    }

}
