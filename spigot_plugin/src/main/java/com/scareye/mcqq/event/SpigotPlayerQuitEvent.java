package com.scareye.mcqq.event;

public class SpigotPlayerQuitEvent extends SpigotNoticeEvent {

    public SpigotPlayerQuitEvent(String server_name, SpigotPlayer player) {
        super(server_name, "PlayerQuitEvent", "quit", player);
    }
}
