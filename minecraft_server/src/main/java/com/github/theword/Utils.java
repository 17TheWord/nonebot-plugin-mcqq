package com.github.theword;
/*
正则
    原版服务器 聊天 判定："\[Server thread/INFO]:(.*)<(.*)> (.*)"
    原版服务端 加入/离开 判定："\[Server thread/INFO] :(.*) (.*) the game"

    Forge端 聊天 判定："\[Server thread/INFO] \[net.Minecraft.server.MinecraftServer/]:(.*)<(.*)> (.*)"
    Forge端 加入/离开 判定："\[Server thread/INFO] \[net.Minecraft.server.MinecraftServer/]: (.*) (.*) the game"

    Forge 1.18.2 聊天 判定："\[Server thread/INFO] \[net.Minecraft.server.dedicated.DedicatedServer/]:(.*)<(.*)> (.*)"
    Forge 1.18.2 加入/离开 判定："\[Server thread/INFO] \[net.Minecraft.server.dedicated.DedicatedServer/]: (.*) (.*) the game"

    Fabric端 与原版日志相同

 */


import com.github.theword.event.MinecraftPlayer;
import com.github.theword.event.MinecraftPlayerChatEvent;
import com.github.theword.event.MinecraftPlayerJoinEvent;
import com.github.theword.event.MinecraftPlayerQuitEvent;
import com.google.gson.Gson;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class Utils {

    public static void say(String message) {
        System.out.println("[MC_QQ] " + message);
    }


    // 正则表达式
    private static final String MINECRAFT_CHAT_REGEX = "(.*)]:(.*)<(.*)> (.*)";
    private static final String MINECRAFT_JOIN_QUIT_REGEX = "(.*)]: (.*) (.*) the game";


    /**
     * 将日志消息处理为Json
     *
     * @param msg 日志消息
     * @return Json
     */
    public static String processEventToJson(String msg) {
        Gson gson = new Gson();

        String text;

        String result;

        if (getServerLogMatcher(msg, MINECRAFT_CHAT_REGEX) != null) {
            Matcher matcher = getServerLogMatcher(msg, MINECRAFT_CHAT_REGEX);
            assert matcher != null;
            MinecraftPlayer player = new MinecraftPlayer(matcher.group(3));
            MinecraftPlayerChatEvent event = new MinecraftPlayerChatEvent("0", player, matcher.group(4));
            result = gson.toJson(event);
            text = event.toString();
        } else if (getServerLogMatcher(msg, MINECRAFT_JOIN_QUIT_REGEX) != null) {
            Matcher matcher = getServerLogMatcher(msg, MINECRAFT_JOIN_QUIT_REGEX);
            assert matcher != null;
            MinecraftPlayer player = new MinecraftPlayer(matcher.group(2));
            if (matcher.group(3).equals("joined")) {
                MinecraftPlayerJoinEvent event = new MinecraftPlayerJoinEvent(player);
                result = gson.toJson(event);
                text = event.toString();
            } else if (matcher.group(3).equals("left")) {
                MinecraftPlayerQuitEvent event = new MinecraftPlayerQuitEvent(player);
                result = gson.toJson(event);
                text = event.toString();
            } else {
                return null;
            }
        } else {
            return null;
        }

        say(text);
        return result;
    }

    // 省略其他方法，保留原有逻辑

    /**
     * 通过正则获取服务器日志
     *
     * @param allText 完整信息
     * @param regex   匹配信息的正则表达式
     * @return Matcher
     */
    private static Matcher getServerLogMatcher(String allText, String regex) {
        Pattern pattern = Pattern.compile(regex);
        Matcher matcher = pattern.matcher(allText);
        if (matcher.find()) {
            return matcher;
        }
        return null;
    }

    /**
     * 字符串转为 unicode 编码
     *
     * @param string 字符串
     * @return unicode编码
     */
    static String unicodeEncode(String string) {
        char[] utfBytes = string.toCharArray();
        StringBuilder unicodeBytes = new StringBuilder();
        for (char utfByte : utfBytes) {
            String hexB = Integer.toHexString(utfByte);
            if (hexB.length() <= 2) {
                hexB = "00" + hexB;
            }
            unicodeBytes.append("\\u").append(hexB);
        }
        return unicodeBytes.toString();
    }
}
