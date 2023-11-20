package com.scareye.mcqq.returnBody;

import com.google.gson.annotations.SerializedName;

public class MsgItem {
    @SerializedName("msg_text")
    private String msgText;
    @SerializedName("color")
    private String color;

    @SerializedName("action_event")
    private ActionEvent actionEvent;

    public String getMsgText() {
        return msgText;
    }

    public void setMsgText(String msgText) {
        this.msgText = msgText;
    }

    public String getColor() {
        return color;
    }

    public void setColor(String color) {
        this.color = color;
    }

    public ActionEvent getActionEvent() {
        return actionEvent;
    }

    public void setActionEvent(ActionEvent actionEvent) {
        this.actionEvent = actionEvent;
    }

    @Override
    public String toString() {
        return "MsgItem{" +
                "msgText='" + msgText + '\'' +
                ", color='" + color + '\'' +
                ", actionEvent=" + actionEvent +
                '}';
    }
}
