package com.github.theword.event;

public class MinecraftPlayerQuitEvent extends MinecraftNoticeEvent {
    public MinecraftPlayerQuitEvent(MinecraftPlayer player) {
        super("MinecraftPlayerQuitEvent", "quit", player);
    }


    @Override
    public String toString() {
        return "[" + this.getPostType() + "] " + this.getPlayer().getNickname() + " quit the game";
    }
}
