package com.github.theword;

import java.net.URISyntaxException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.Map;

import static com.github.theword.Utils.say;

public class MCQQ {
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
        Path configMapFilePath = Paths.get((String) ConfigReader.config().get("log_local"), (String) ConfigReader.config().get("log_name"));

        if (!configMapFilePath.toFile().exists()) {
            say("日志文件不存在，请检查配置文件。");
            return;
        }

        FileWatcher.FileListen((String) ConfigReader.config().get("log_local"), (String) ConfigReader.config().get("log_name"));
        // 连接次数初始化为 0
        connectTime = 0;

        try {
            wsClient = new WSClient();
            wsClient.connect();
        } catch (URISyntaxException e) {
            say("WebSocket URL 地址非法，请检查配置文件。");
        }
    }

}
