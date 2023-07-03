package com.scareye.mcqq.event;

public class SpigotPlayerDeathEvent extends SpigotMessageEvent {
    private String death_message;

    public String getDeath_message() {
        return death_message;
    }

    public void setDeath_message(String death_message) {
        this.death_message = death_message;
    }

    public SpigotPlayerDeathEvent(String server_name, SpigotPlayer player, String death_message) {
        super(server_name, "PlayerDeathEvent", "death", player);
        this.death_message = death_message;
    }
}
