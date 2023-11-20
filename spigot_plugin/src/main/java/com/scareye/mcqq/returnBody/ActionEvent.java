package com.scareye.mcqq.returnBody;

import com.google.gson.annotations.SerializedName;

public class ActionEvent {

    @SerializedName("click_event_url")
    private String clickEventUrl;

    @SerializedName("hover_event_text")
    private String hoverEventText;

    public String getClickEventUrl() {
        return clickEventUrl;
    }

    public void setClickEventUrl(String clickEventUrl) {
        this.clickEventUrl = clickEventUrl;
    }

    public String getHoverEventText() {
        return hoverEventText;
    }

    public void setHoverEventText(String hoverEventText) {
        this.hoverEventText = hoverEventText;
    }

    @Override
    public String toString() {
        return "ActionEvent{" +
                "clickEventUrl='" + clickEventUrl + '\'' +
                ", hoverEventText='" + hoverEventText + '\'' +
                '}';
    }
}
