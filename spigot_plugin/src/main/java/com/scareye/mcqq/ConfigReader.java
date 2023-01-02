package com.scareye.mcqq;


import org.bukkit.configuration.file.FileConfiguration;

class ConfigReader {

    /**
     * 获取配置文件信息
     */
    static FileConfiguration config = MC_QQ.instance.getConfig();

    /**
     * 获取是否启用插件
     *
     * @return boolean Enable
     */
    static boolean getEnable() {
        return config.getBoolean("enable_mc_qq", true);
    }

    /**
     * 获取服务器名
     *
     * @return String serverName
     */
    static String getServerName() {
        return config.getString("server_name", "");
    }

    /**
     * 获取地址
     *
     * @return String Address
     */
    static String getAddress() {
        return config.getString("websocket_hostname", "127.0.0.1");
    }

    /**
     * 获取端口
     *
     * @return int Port
     */
    static int getPort() {
        return config.getInt("websocket_port", Integer.parseInt("8765"));
    }

    /**
     * 获取聊天修饰
     *
     * @return String SayWay
     */
    static String getSayWay() {
        return config.getString("say_way", "说：");
    }

    /**
     * 获取是否启用 死亡事件 推送
     *
     * @return boolean deathMessage
     */
    static boolean getDeathMessage() {
        return getEnable() &&config.getBoolean("death_message", true);
    }

    /**
     * 获取是否启用 加入/退出 推送
     *
     * @return boolean JoinQuit
     */
    static boolean getJoinQuit() {
        return getEnable() &&config.getBoolean("join_quit", true);
    }

    /**
     * 获取是否启用 群名/频道名 前缀
     *
     * @return boolean JoinQuit
     */
    static boolean getDisplayServerName() {
        return getEnable() && config.getBoolean("display_servername", false);
    }

}
