package com.github.theword.event;

import lombok.Getter;

@Getter
public class MinecraftPlayer {
    private final String nickname;

    public MinecraftPlayer(String nickname) {
        this.nickname = nickname;
    }

    @Override
    public String toString() {
        return this.nickname;
    }
}
