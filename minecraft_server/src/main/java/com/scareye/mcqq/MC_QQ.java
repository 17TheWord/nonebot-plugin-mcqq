package com.scareye.mcqq;

import java.net.UnknownHostException;

public class MC_QQ {
    static Ws websocket;
    static ConfigReader configReader;


    public static void main(String[] args) {
        configReader = new ConfigReader();
        FileWatcher.FileListen((String) configReader.config().get("log_local"), "latest.log");
        try {
            websocket = new Ws();
        } catch (UnknownHostException e) {
            throw new RuntimeException(e);
        }
        websocket.start();
    }

}
