package com.scareye.mcqq;

import java.net.UnknownHostException;

public class MC_QQ {
    static Ws websocket;
    static ConfigReader configReader;


    public static void main(String[] args) {
        FileWatcher.FileListen(".\\logs\\", "latest.log");
        configReader = new ConfigReader();
        try {
            websocket = new Ws((String) configReader.config().get("websocket_hostname"), (Integer) configReader.config().get("websocket_port"));
        } catch (UnknownHostException e) {
            throw new RuntimeException(e);
        }
        websocket.start();
    }

}
