package com.github.theword.event;

public class MinecraftPlayerJoinEvent extends MinecraftNoticeEvent {
    public MinecraftPlayerJoinEvent(MinecraftPlayer player) {
        super("MinecraftPlayerJoinEvent", "join", player);
    }

    @Override
    public String toString() {
        return "[" + this.getPostType() + "] " + this.getPlayer().getNickname() + " joined the game";
    }

}
