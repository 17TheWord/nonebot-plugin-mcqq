package com.scareye.mcqq;
/*
正则
    原版服务器 聊天 判定："\[Server thread/INFO]:(.*)<(.*)> (.*)"
    原版服务端 加入/离开 判定："\[Server thread/INFO] :(.*) (.*) the game"
    Forge端 聊天 判定："\[Server thread/INFO] \[net.minecraft.server.MinecraftServer/]:(.*)<(.*)> (.*)"
    Forge端 加入/离开 判定："\[Server thread/INFO] \[net.minecraft.server.MinecraftServer/]: (.*) (.*) the game"
    Fabric端 与原版日志相同
 */

import com.alibaba.fastjson.JSONObject;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

import static com.scareye.mcqq.ConfigReader.config;

public class Utils {

    /**
     * 原版端 聊天 正则
     */
    static String minecraftChatRegex = "\\[Server thread/INFO]:(.*)<(.*)> (.*)";

    /**
     * 原版端 加入/离开 服务器 正则
     */
    static String minecraftJoinQuitRegex = "\\[Server thread/INFO]: (.*) (.*) the game";

    /**
     * Forge端 聊天 正则
     */
    static String forgeChatRegex = "\\[Server thread/INFO] \\[net.minecraft.server.MinecraftServer/]:(.*)<(.*)> (.*)";

    /**
     * Forge端 加入/离开 服务器 正则
     */
    static String forgeJoinQuitRegex = "\\[Server thread/INFO] \\[net.minecraft.server.MinecraftServer/]: (.*) (.*) the game";

    /**
     * 向服务器后台发送信息
     *
     * @param msg String 信息
     */
    static void say(String msg) {
        System.out.println(("[MC_QQ]丨" + msg));
    }

    /**
     * 将 日志消息 处理为 Json
     *
     * @param msg String 日志消息
     * @return String Json
     */
    static String processMessageToJson(String msg) {

        JSONObject jsonMessage = new JSONObject();
        JSONObject messageJson = new JSONObject();
        String text_msg = "";

        // 如果服务器名为设置，则不添加至 text_msg 文本
        if (!config().get("server_name").equals("")) {
            text_msg = "[" + config().get("server_name") + "] ";
        }

        // 放入服务器名
        jsonMessage.put("server_name", config().get("server_name"));

        Matcher serverLog = null;

        // 判定前缀
        if (getIfMinecraftChat(msg) || getIfForgeChat(msg)) {
            /*
            聊天
             */
            String playerName;
            String playerMsg;
            if (getIfMinecraftChat(msg)) {
                // 原版聊天
                serverLog = getServerLogMatcher(msg, minecraftChatRegex);
            } else if (getIfForgeChat(msg)) {
                serverLog = getServerLogMatcher(msg, forgeChatRegex);
            }
            playerName = serverLog.group(2);
            playerMsg = serverLog.group(3);


            // 放入事件名
            jsonMessage.put("event_name", "AsyncPlayerChatEvent");
            // 放入玩家
            jsonMessage.put("player", new JSONObject().put("nickname", playerName));

            // message的Json
            messageJson.put("type", "text");
            messageJson.put("data", playerName + config().get("say_way") + playerMsg);
            jsonMessage.put("message", messageJson);

            text_msg += playerName + config().get("say_way") + playerMsg;

        } else if ((Boolean) config().get("join_quit") && (getIfMinecraftJoinQuit(msg) || getIfForgeJoinQuit(msg))) {
            /*
            加入/离开服务器
             */
            String playerName;
            String join_quit_msg;
            String data = "";
            if (getIfMinecraftJoinQuit(msg)) {
                /*
                原版
                 */
                serverLog = getServerLogMatcher(msg, minecraftJoinQuitRegex);
            } else if (getIfForgeJoinQuit(msg)) {
                /*
                Forge
                 */
                serverLog = getServerLogMatcher(msg, minecraftJoinQuitRegex);
            }
            playerName = serverLog.group(1);
            join_quit_msg = serverLog.group(2);
            if (join_quit_msg.equals("joined")) {
                jsonMessage.put("event_name", "PlayerJoinEvent");
                data = playerName + " 加入了服务器";
            } else if (join_quit_msg.equals("left")) {
                jsonMessage.put("event_name", "PlayerQuitEvent");
                data = playerName + " 离开了服务器";
            }

            // 写入message
            messageJson.put("type", "text");
            messageJson.put("data", data);
            jsonMessage.put("message", messageJson);

            text_msg += data;
        }
        say(text_msg);
        return jsonMessage.toJSONString();
    }

    /**
     * 获取 是否为 原版端 聊天 消息
     *
     * @param message String 消息
     * @return boolean
     */
    static boolean getIfMinecraftChat(String message) {
        Pattern pattern = Pattern.compile(minecraftChatRegex);
        Matcher matcher = pattern.matcher(message);
        return matcher.find();
    }

    /**
     * 获取 是否为 原版端 加入/离开 消息
     *
     * @param message String 消息
     * @return boolean
     */
    static boolean getIfMinecraftJoinQuit(String message) {
        Pattern pattern = Pattern.compile(minecraftJoinQuitRegex);
        Matcher matcher = pattern.matcher(message);
        return matcher.find();
    }

    /**
     * 获取 是否为 Forge端 聊天 消息
     *
     * @param message String 消息
     * @return boolean
     */
    static boolean getIfForgeChat(String message) {
        Pattern pattern = Pattern.compile(forgeChatRegex);
        Matcher matcher = pattern.matcher(message);
        return matcher.find();
    }

    /**
     * 获取 是否为 Forge端 加入/离开 消息
     *
     * @param message String 消息
     * @return boolean
     */
    static boolean getIfForgeJoinQuit(String message) {
        Pattern pattern = Pattern.compile(forgeJoinQuitRegex);
        Matcher matcher = pattern.matcher(message);
        return matcher.find();
    }

    /**
     * 获取 是否为需要的信息
     *
     * @param message 信息
     * @return boolean
     */
    static boolean getIfNeedMsg(String message) {
        return getIfMinecraftChat(message) || getIfMinecraftJoinQuit(message) || getIfForgeChat(message) || getIfForgeJoinQuit(message);
    }

    /**
     * 通过正则获取服务器日志
     *
     * @param allText 完整信息
     * @param text    匹配信息 正则
     * @return Matcher
     */
    public static Matcher getServerLogMatcher(String allText, String text) {
        Pattern pattern = Pattern.compile(text);
        Matcher matcher = pattern.matcher(allText);
        if (matcher.find()) {
            return matcher;
        }
        return null;
    }


}
