package com.scareye.mcqq.event;

public class SpigotPlayer {

    private String uuid;
    private String nickname;
    private String display_name;
    private String player_list_name;
    private String address;

    private boolean is_health_scaled;

    private double health_scale;

    private float exp;

    private int total_exp;
    private int level;

    private String locale;

    private int ping;

    private long player_time;

    private boolean is_player_time_relative;

    private long player_time_offset;

    private float walk_speed;
    private float fly_speed;
    private boolean allow_flight;
    private boolean is_sprinting;
    private boolean is_sneaking;
    private boolean is_flying;

    private boolean is_op;

    public String getUuid() {
        return uuid;
    }

    public void setUuid(String uuid) {
        this.uuid = uuid;
    }

    public String getNickname() {
        return nickname;
    }

    public void setNickname(String nickname) {
        this.nickname = nickname;
    }

    public String getDisplay_name() {
        return display_name;
    }

    public void setDisplay_name(String display_name) {
        this.display_name = display_name;
    }

    public String getPlayer_list_name() {
        return player_list_name;
    }

    public void setPlayer_list_name(String player_list_name) {
        this.player_list_name = player_list_name;
    }

    public String getAddress() {
        return address;
    }

    public void setAddress(String address) {
        this.address = address;
    }

    public boolean isIs_health_scaled() {
        return is_health_scaled;
    }

    public void setIs_health_scaled(boolean is_health_scaled) {
        this.is_health_scaled = is_health_scaled;
    }

    public double getHealth_scale() {
        return health_scale;
    }

    public void setHealth_scale(double health_scale) {
        this.health_scale = health_scale;
    }

    public float getExp() {
        return exp;
    }

    public void setExp(float exp) {
        this.exp = exp;
    }

    public int getTotal_exp() {
        return total_exp;
    }

    public void setTotal_exp(int total_exp) {
        this.total_exp = total_exp;
    }

    public int getLevel() {
        return level;
    }

    public void setLevel(int level) {
        this.level = level;
    }

    public String getLocale() {
        return locale;
    }

    public void setLocale(String locale) {
        this.locale = locale;
    }

    public int getPing() {
        return ping;
    }

    public void setPing(int ping) {
        this.ping = ping;
    }

    public long getPlayer_time() {
        return player_time;
    }

    public void setPlayer_time(long player_time) {
        this.player_time = player_time;
    }

    public boolean isIs_player_time_relative() {
        return is_player_time_relative;
    }

    public void setIs_player_time_relative(boolean is_player_time_relative) {
        this.is_player_time_relative = is_player_time_relative;
    }

    public long getPlayer_time_offset() {
        return player_time_offset;
    }

    public void setPlayer_time_offset(long player_time_offset) {
        this.player_time_offset = player_time_offset;
    }

    public float getWalk_speed() {
        return walk_speed;
    }

    public void setWalk_speed(float walk_speed) {
        this.walk_speed = walk_speed;
    }

    public float getFly_speed() {
        return fly_speed;
    }

    public void setFly_speed(float fly_speed) {
        this.fly_speed = fly_speed;
    }

    public boolean isAllow_flight() {
        return allow_flight;
    }

    public void setAllow_flight(boolean allow_flight) {
        this.allow_flight = allow_flight;
    }

    public boolean isIs_sprinting() {
        return is_sprinting;
    }

    public void setIs_sprinting(boolean is_sprinting) {
        this.is_sprinting = is_sprinting;
    }

    public boolean isIs_sneaking() {
        return is_sneaking;
    }

    public void setIs_sneaking(boolean is_sneaking) {
        this.is_sneaking = is_sneaking;
    }

    public boolean isIs_flying() {
        return is_flying;
    }

    public void setIs_flying(boolean is_flying) {
        this.is_flying = is_flying;
    }

    public boolean isIs_op() {
        return is_op;
    }

    public void setIs_op(boolean is_op) {
        this.is_op = is_op;
    }

    public SpigotPlayer() {
    }

    public SpigotPlayer(String uuid, String nickname, String display_name, String player_list_name, String address, boolean is_health_scaled, double health_scale, float exp, int total_exp, int level, String locale, int ping, long player_time, boolean is_player_time_relative, long player_time_offset, float walk_speed, float fly_speed, boolean allow_flight, boolean is_sprinting, boolean is_sneaking, boolean is_flying, boolean is_op) {
        this.uuid = uuid;
        this.nickname = nickname;
        this.display_name = display_name;
        this.player_list_name = player_list_name;
        this.address = address;
        this.is_health_scaled = is_health_scaled;
        this.health_scale = health_scale;
        this.exp = exp;
        this.total_exp = total_exp;
        this.level = level;
        this.locale = locale;
        this.ping = ping;
        this.player_time = player_time;
        this.is_player_time_relative = is_player_time_relative;
        this.player_time_offset = player_time_offset;
        this.walk_speed = walk_speed;
        this.fly_speed = fly_speed;
        this.allow_flight = allow_flight;
        this.is_sprinting = is_sprinting;
        this.is_sneaking = is_sneaking;
        this.is_flying = is_flying;
        this.is_op = is_op;
    }
}
