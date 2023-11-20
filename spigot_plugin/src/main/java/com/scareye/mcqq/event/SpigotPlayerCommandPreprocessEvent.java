package com.scareye.mcqq.event;

public class SpigotPlayerCommandPreprocessEvent extends SpigotMessageEvent {

    public SpigotPlayerCommandPreprocessEvent(String server_name, SpigotPlayer player, String command) {
        super(server_name, "PlayerCommandPreprocessEvent", "player_command", player, command);
    }
}
