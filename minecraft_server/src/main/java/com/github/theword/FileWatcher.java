package com.github.theword;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.RandomAccessFile;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.List;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.Consumer;

import static com.github.theword.MCQQ.wsClient;
import static com.github.theword.ConfigReader.config;
import static com.github.theword.Utils.processEventToJson;
import static com.github.theword.Utils.say;

/**
 * 监控文件变化
 *
 * @author YL
 **/
public class FileWatcher {

    /**
     * 文件监听
     *
     * @param filePath 文件路径
     * @param fileName 文件名称
     */
    public static void FileListen(String filePath, String fileName) {
        // 监控的目录

        // 这里监听
        new Thread(() -> {
            try {
                FileWatcher.watcherLog(filePath, fileName, str -> System.out.println((System.currentTimeMillis() / 1000) + ",监听到: " + str));
            } catch (Exception e) {
                System.err.println("[MC_QQ] 监听日志错误：" + e);
                e.printStackTrace();
            }
        }).start();

        // 这里写
        new Thread(() -> {
            try {
//                int i = 0;
                while (true) {
                    FileWriter writer = new FileWriter(filePath + fileName, true);
//                    Thread.sleep(1000);
//                    writer.append(String.valueOf(i)).append("\n");
                    writer.flush();
                    // 刷完关闭在下次循环重新打开。这样效果好
                    // 否则系统可能会批量刷盘，上面的监听效果就是 一批一批一，分批过来的
                    writer.close();
//                    i ++;
                }
            } catch (IOException e) {
                System.err.println("[MC_QQ] 监听日志错误：" + e);
            }
        }).start();
    }

    /**
     * 文件监控
     * 同步调用会阻塞
     *
     * @param filePath String
     * @param fileName String
     * @param consumer consumer<String>
     * @throws IOException          异常
     * @throws InterruptedException 异常
     */
    public static void watcherLog(String filePath, String fileName, Consumer<String> consumer) throws IOException, InterruptedException {
        WatchService watchService = FileSystems.getDefault().newWatchService();

        Paths.get(filePath).register(watchService, StandardWatchEventKinds.ENTRY_CREATE, StandardWatchEventKinds.ENTRY_MODIFY, StandardWatchEventKinds.ENTRY_DELETE);
        // 文件读取行数
        AtomicLong lastPointer = new AtomicLong(0L);
        do {
            WatchKey key = watchService.take();
            List<WatchEvent<?>> watchEvents = key.pollEvents();
            watchEvents.stream().filter(i -> StandardWatchEventKinds.ENTRY_MODIFY == i.kind() && fileName.equals(((Path) i.context()).getFileName().toString())).forEach(i -> {
                if (i.count() > 1) {
                    // "重复事件"
                    return;
                }

                File configFile = Paths.get(filePath + "/" + i.context()).toFile();
                StringBuilder str = new StringBuilder();
                // 读取文件
                lastPointer.set(getFileContent(configFile, lastPointer.get(), str));

                // 消息转为 String
                String msg = str.toString();


                if (!msg.equals("") && msg.length() < 320) {

                    if ((Boolean) config().get("log_debug")) {
                        say("监听到日志变更：" + msg);
                    }

                    // 发送处理过的消息
                    if ((Boolean) config().get("enable_mc_qq")) {
                        if (processEventToJson(msg) != null) {
                            String result = processEventToJson(msg);

                            if ((Boolean) config().get("log_debug")) {
                                say("消息处理结果：" + result);
                            }

                            wsClient.sendMessage(result);
                        }
                    }
                }

//                if (str.length() != 0) {
//                    consumer.accept(str.toString());
//                }
            });
            key.reset();
        } while (true);
    }

    /**
     * beginPointer > configFile 时会从头读取
     *
     * @param configFile   配置文件
     * @param beginPointer 起点
     * @param str          内容会拼接进去
     * @return 读到了多少字节, -1 读取失败
     */
    private static long getFileContent(File configFile, long beginPointer, StringBuilder str) {
        if (beginPointer < 0) {
            beginPointer = 0;
        }
        RandomAccessFile file = null;
        boolean top = true;
        try {
            file = new RandomAccessFile(configFile, "r");
            if (beginPointer > file.length()) {
                return 0;
            }
            file.seek(beginPointer);
            String line;
            while ((line = file.readLine()) != null) {
                if (top) {
                    top = false;
                } else {
                    str.append("\n");
                }
                str.append(new String(line.getBytes(StandardCharsets.ISO_8859_1), "GBK"));
            }
            return file.getFilePointer();
        } catch (IOException e) {
            e.printStackTrace();
            return -1;
        } finally {
            if (file != null) {
                try {
                    file.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }
    }
}