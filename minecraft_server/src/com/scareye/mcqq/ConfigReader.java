package com.scareye.mcqq;


import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

import org.yaml.snakeyaml.Yaml;

public class ConfigReader {
    public static Map<String, Object> config() {
        File configFile = new File("config.yml");
        Map<String, Object> configMap;
        try {
            FileReader reader = new FileReader(configFile);
            BufferedReader buffer = new BufferedReader(reader);
            configMap = new Yaml().load(buffer);
            buffer.close();
            reader.close();
            return configMap;
        } catch (IOException e) {
            configMap = new HashMap<>();
            configMap.put("enable_mc_qq", true);
            configMap.put("websocket_hostname", "127.0.0.1");
            configMap.put("websocket_port", "8765");
            configMap.put("say_way", " 说：");
            configMap.put("death_message", true);
            configMap.put("join_quit", true);
            configMap.put("server_name", "");
            configMap.put("display_groupname", false);
            configMap.put("log_local", ".\\logs\\");
            configMap.put("log_name", "latest.log");
            return configMap;
        }
    }
}