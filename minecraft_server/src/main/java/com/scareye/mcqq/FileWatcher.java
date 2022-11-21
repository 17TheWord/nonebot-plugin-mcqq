package com.scareye.mcqq;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.RandomAccessFile;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.List;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.Consumer;

import static com.scareye.mcqq.MC_QQ.configReader;

/**
 * 监控文件变化
 *
 * @author YL
 **/
public class FileWatcher {

    public static void FileListen(String filePath, String fileName) {
        // 监控的目录

        // 这里监听
        new Thread(() -> {
            try {
                FileWatcher.watcherLog(filePath, fileName, str -> System.out.println((System.currentTimeMillis() / 1000) + ",监听到: " + str));
            } catch (Exception e) {
                e.printStackTrace();
            }
        }).start();

        // 这里写
        new Thread(() -> {
            try {
//                int i = 0;
                while (true) {
                    FileWriter writer = new FileWriter(filePath + fileName, true);
                    Thread.sleep(1000);
//                    writer.append(String.valueOf(i)).append("\n");
                    writer.flush();
                    // 刷完关闭在下次循环重新打开。这样效果好
                    // 否则系统可能会批量刷盘，上面的监听效果就是 一批一批一，分批过来的
                    writer.close();
//                    i ++;
                }
            } catch (IOException | InterruptedException e) {
                e.printStackTrace();
            }
        }).start();
    }

    /**
     * 文件监控
     * 同步调用会阻塞
     *
     * @param filePath
     * @param fileName
     * @param consumer
     * @throws IOException
     * @throws InterruptedException
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

                // 消息处理
                /*
                原版服务器聊天内容判定："[Async Chat Thread - "
                原版服务端加入/离开判定："[Server thread/INFO]:"
                Forge端聊天内容判定："[Server thread/INFO] [net.minecraft.server.dedicated.DedicatedServer/]: <Yuuuo> ."
                Forge端加入/离开判定："[Server thread/INFO] [net.minecraft.server.dedicated.DedicatedServer/]: Yuuuo joined the game"
                 */
                if ((Boolean) configReader.config().get("enable_mc_qq") && msg.length() < 256) {
                    // 判定前缀
                    if (msg.contains("[Server thread/INFO] [net.minecraft.server.dedicated.DedicatedServer/]: <")) {
                        String playerName = msg.substring(msg.indexOf("[Server thread/INFO] [net.minecraft.server.dedicated.DedicatedServer/]: <") + "[Server thread/INFO] [net.minecraft.server.dedicated.DedicatedServer/]: <".length(), msg.indexOf(">"));
                        String playerMsg = msg.substring(msg.indexOf(playerName + "> ") + (playerName + "> ").length());
                        MC_QQ.websocket.sendMessage(playerName + configReader.config().get("say_way") + playerMsg);
                    } else if (msg.contains("[Async Chat Thread - ")) {
                        String playerName = msg.substring(msg.indexOf("/INFO]: <") + 9, msg.indexOf(">"));
                        String playerMsg = msg.substring(msg.indexOf(playerName + "> ") + (playerName + "> ").length());
                        MC_QQ.websocket.sendMessage(playerName + configReader.config().get("say_way") + playerMsg);
                    }
                    boolean join_left = msg.contains(" left the game") | msg.contains(" joined the game");
                    if ((Boolean) configReader.config().get("join_quit")) {
                        if (msg.contains("[Server thread/INFO] [net.minecraft.server.dedicated.DedicatedServer/]: ") & join_left) {
                            String join_quit_msg = msg.substring(msg.indexOf("[Server thread/INFO] [net.minecraft.server.dedicated.DedicatedServer/]: ") + "[Server thread/INFO] [net.minecraft.server.dedicated.DedicatedServer/]: ".length());
                            if (join_quit_msg.contains(" left the game")) {
                                join_quit_msg = join_quit_msg.replace("left the game", "离开了服务器");
                            } else {
                                join_quit_msg = join_quit_msg.replace("joined the game", "加入了服务器");
                            }
                            MC_QQ.websocket.sendMessage(join_quit_msg);
                        }
                    } else if ((Boolean) configReader.config().get("join_quit")) {
                        if (msg.contains("[Server thread/INFO]: ") & join_left) {
                            String join_quit_msg = msg.substring(msg.indexOf("[Server thread/INFO]: ") + "[Server thread/INFO]: ".length());
                            if (join_quit_msg.contains(" left the game")) {
                                join_quit_msg = join_quit_msg.replace("left the game", "离开了服务器");
                            } else {
                                join_quit_msg = join_quit_msg.replace("joined the game", "加入了服务器");
                            }
                            MC_QQ.websocket.sendMessage(join_quit_msg);
                        }
                    }
                }

                if (str.length() != 0) {
                    consumer.accept(str.toString());
                }
            });
            key.reset();
        } while (true);
    }

    /**
     * beginPointer > configFile 时会从头读取
     *
     * @param configFile
     * @param beginPointer
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


