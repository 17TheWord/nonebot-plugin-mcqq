package com.github.theword;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.Map;

import org.yaml.snakeyaml.Yaml;

import static com.github.theword.Utils.say;

public class ConfigReader {
    public static Map<String, Object> config() {
        Path configMapFilePath = Paths.get("config", "mcqq", "config.yml");

        if (!Files.exists(configMapFilePath)) {
            say("配置文件不存在，正在创建...");
            try {
                Files.createDirectories(configMapFilePath.getParent());
                say("创建目录成功");
                try (InputStream inputStream = MCQQ.class.getClassLoader().getResourceAsStream("config.yml")) {
                    assert inputStream != null;
                    Files.copy(inputStream, configMapFilePath);
                    say("创建配置文件成功");
                }
            } catch (IOException e) {
                say("创建配置文件失败，原因：" + e.getMessage());
            }
        }

        Map<String, Object> configMap;

        try {
            Reader reader = Files.newBufferedReader(configMapFilePath);
            BufferedReader buffer = new BufferedReader(reader);
            configMap = new Yaml().load(buffer);
            buffer.close();
            reader.close();
            return configMap;
        } catch (IOException e) {
            say("读取配置文件失败，将使用默认配置。");
            configMap = new HashMap<>();
            configMap.put("enable_mc_qq", true);
            configMap.put("enable_reconnect_msg", true);
            configMap.put("websocket_url", "ws://127.0.0.1:8080/minecraft/ws");
            configMap.put("say_way", " 说：");
            configMap.put("command_message", false);
            configMap.put("death_message", true);
            configMap.put("join_quit", true);
            configMap.put("server_name", "Server");
            configMap.put("log_local", ".\\logs\\");
            configMap.put("log_name", "latest.log");
            configMap.put("log_debug", false);
            return configMap;
        }
    }
}
