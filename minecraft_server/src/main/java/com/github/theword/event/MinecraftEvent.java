package com.github.theword.event;

import com.google.gson.annotations.SerializedName;
import lombok.Getter;

import static com.github.theword.ConfigReader.config;

@Getter
public class MinecraftEvent {
    @SerializedName("server_name")
    private final String serverName = (String) config().get("server_name");
    @SerializedName("event_name")
    private final String eventName;
    @SerializedName("post_type")
    private final String postType;
    @SerializedName("sub_type")
    private final String subType;
    private final int timestamp = (int) (System.currentTimeMillis() / 1000);

    public MinecraftEvent(String eventName, String postType, String subType) {
        this.eventName = eventName;
        this.postType = postType;
        this.subType = subType;
    }

    @Override
    public String toString() {
        return "MinecraftEvent{" +
                "serverName='" + serverName + '\'' +
                ", eventName='" + eventName + '\'' +
                ", postType='" + postType + '\'' +
                ", subType='" + subType + '\'' +
                ", timestamp=" + timestamp +
                '}';
    }
}
