package com.github.theword.event;

import com.google.gson.annotations.SerializedName;
import lombok.Getter;

@Getter
public class MinecraftMessageEvent extends MinecraftEvent {

    @SerializedName("message_id")
    private String messageId;
    private final MinecraftPlayer player;
    private final String message;

    public MinecraftMessageEvent(String eventName, String subType, String messageId, MinecraftPlayer player, String message) {
        super(eventName, "message", subType);
        this.messageId = messageId;
        this.player = player;
        this.message = message;
    }

    @Override
    public String toString() {
        return "[" + this.getPostType() + "] " + this.player.getNickname() + ": " + this.message;
    }
}
