package com.scareye.mcqq.event;

public class SpigotEvent {
    private String server_name;
    private String event_name;
    private String post_type;
    private String sub_type;

    public String getServer_name() {
        return server_name;
    }

    public void setServer_name(String server_name) {
        this.server_name = server_name;
    }

    public String getEvent_name() {
        return event_name;
    }

    public void setEvent_name(String event_name) {
        this.event_name = event_name;
    }

    public String getPost_type() {
        return post_type;
    }

    public void setPost_type(String post_type) {
        this.post_type = post_type;
    }

    public String getSub_type() {
        return sub_type;
    }

    public void setSub_type(String sub_type) {
        this.sub_type = sub_type;
    }

    public SpigotEvent() {
    }

    public SpigotEvent(String server_name, String event_name, String post_type, String sub_type) {
        this.server_name = server_name;
        this.event_name = event_name;
        this.post_type = post_type;
        this.sub_type = sub_type;
    }
}
