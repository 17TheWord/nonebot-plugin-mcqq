package com.scareye.mcqq;

import org.bukkit.Bukkit;
import org.bukkit.command.CommandSender;
import org.bukkit.plugin.java.JavaPlugin;

import java.net.UnknownHostException;


public final class MC_QQ extends JavaPlugin {
    // 静态变量 websocket
    static Ws websocket;

    // 静态变量 instance
    static JavaPlugin instance;

    @Override
    public void onLoad() {
        // 如果配置文件不存在，Bukkit 会保存默认的配置
        saveDefaultConfig();
    }

    @Override
    public void onEnable() {
        // 赋值插件实例
        instance = this;

        // new Ws 对象，并将配置文件中 地址 与 端口 写入
        try {
            websocket = new Ws(ConfigReader.getAddress(), ConfigReader.getPort());
        } catch (UnknownHostException e) {
            throw new RuntimeException(e);
        }
        // 启动 WebSocket
        websocket.start();
        // 注册事件
        Bukkit.getPluginManager().registerEvents(new EventProcessor(), this);
        say("[MC_QQ]：已加载");
    }

    @Override
    public void onDisable() {
        // Plugin shutdown logic
        try {
            websocket.stop();
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        }
        say("[MC_QQ]：已卸载");
    }

    /**
     * 定义方法 Say()
     * 向服务器后台发送信息
     */
    static void say(String msg) {
        CommandSender sender = Bukkit.getConsoleSender();
        sender.sendMessage(msg);
    }
}
