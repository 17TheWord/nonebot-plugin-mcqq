package com.scareye.mcqq;

import java.net.URISyntaxException;

import static com.scareye.mcqq.ConfigReader.config;

public class MC_QQ {
    // 静态变量 wsClient
    static WSClient wsClient;

    // 连接次数
    static int connectTime;


    public static void main(String[] args) {
        // 监听日志文件
        FileWatcher.FileListen((String) config().get("log_local"), (String) config().get("log_name"));
        // 连接次数初始化为 0
        connectTime = 0;
        try {
            wsClient = new WSClient();
            wsClient.connect();
        } catch (URISyntaxException e) {
            e.printStackTrace();
        }
    }

}
