package com.scareye.mcqq;


import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.util.Map;

import org.yaml.snakeyaml.Yaml;

public class ConfigReader {
    public Map<String, Object> config() {
        File configFile = new File("config.yml");

        if (!configFile.exists()) {
            System.err.println("配置文件不存在，请创建。");
        }
        try {
            FileReader reader = new FileReader(configFile);
            BufferedReader buffer = new BufferedReader(reader);
            Map<String, Object> configMap = new Yaml().load(buffer);
            buffer.close();
            reader.close();
            return configMap;
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }
}