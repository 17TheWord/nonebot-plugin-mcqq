package com.scareye.mcqq.returnBody;

import com.google.gson.annotations.SerializedName;

import java.util.List;

public class MinecraftReturnBody {

    @SerializedName("message")
    private List<MsgItem> message;

    public List<MsgItem> getMessage() {
        return message;
    }

    public void setMessage(List<MsgItem> message) {
        this.message = message;
    }

    @Override
    public String toString() {
        return "MinecraftReturnBody{" +
                "message=" + message +
                '}';
    }
}

