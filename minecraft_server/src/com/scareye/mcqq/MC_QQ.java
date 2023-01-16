package com.scareye.mcqq;

import java.net.URISyntaxException;
import java.util.HashMap;
import java.util.Map;

import static com.scareye.mcqq.ConfigReader.config;

public class MC_QQ {
    // 静态变量 wsClient
    static WSClient wsClient;

    // 连接次数
    static int connectTime;

    // WebSocket连接头部信息
    static Map<String, String> httpHeaders;

    public static void main(String[] args) {
        // 监听日志文件
        FileWatcher.FileListen((String) config().get("log_local"), (String) config().get("log_name"));
        // 连接次数初始化为 0
        connectTime = 0;

        // WebSocket 头部信息
        httpHeaders = new HashMap<>();
        httpHeaders.put("x-self-name", (String) config().get("server_name"));

        try {
            wsClient = new WSClient();
            wsClient.connect();
        } catch (URISyntaxException e) {
            e.printStackTrace();
        }
    }

}
