package com.scareye.mcqq;

import java.net.URISyntaxException;
import java.util.HashMap;
import java.util.Map;


public class MC_QQ {
    // 静态变量 wsClient
    static WSClient wsClient;

    // 连接次数
    static int connectTime;

    // WebSocket连接头部信息
    static Map<String, String> httpHeaders;

    public static void main(String[] args) {
        // WebSocket 头部信息
        httpHeaders = new HashMap<>();
        httpHeaders.put("x-self-name", Utils.unicodeEncode(String.valueOf(ConfigReader.config().get("server_name"))));

        // 监听日志文件
        FileWatcher.FileListen((String) ConfigReader.config().get("log_local"), (String) ConfigReader.config().get("log_name"));
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
