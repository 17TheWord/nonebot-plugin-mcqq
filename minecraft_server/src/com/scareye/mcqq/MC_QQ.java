package com.scareye.mcqq;

public class MC_QQ {
    static Ws websocket;
    static ConfigReader configReader;


    public static void main(String[] args) {
        configReader = new ConfigReader();
        FileWatcher.FileListen((String) configReader.config().get("log_local"), "latest.log");
        websocket = new Ws();
        websocket.start();
    }

}
