package com.scareye.mcqq.event;

public class SpigotPlayerDeathEvent extends SpigotMessageEvent {

    public SpigotPlayerDeathEvent(String server_name, SpigotPlayer player, String message) {
        super(server_name, "PlayerDeathEvent", "death", player, message);
    }
}
