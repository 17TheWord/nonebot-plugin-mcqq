package com.github.theword.event;

import lombok.Getter;

@Getter
public class MinecraftNoticeEvent extends MinecraftEvent {

    private final MinecraftPlayer player;

    public MinecraftNoticeEvent(String eventName, String subType, MinecraftPlayer player) {
        super(eventName, "notice", subType);
        this.player = player;
    }

    @Override
    public String toString() {
        return "[" + this.getPostType() + "] " + this.player.getNickname();
    }
}
