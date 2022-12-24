package com.scareye.mcqq;

import org.java_websocket.WebSocket;
import org.java_websocket.handshake.ClientHandshake;
import org.java_websocket.server.WebSocketServer;

import java.net.InetSocketAddress;
import java.net.UnknownHostException;

import static com.scareye.mcqq.MC_QQ.websocket;
import static com.scareye.mcqq.MC_QQ.configReader;


class Ws extends WebSocketServer {
    // 用于获取 WebSocket 的 wb 变量
    WebSocket wb;

    // 连接状态
    boolean ifOpen;


    Ws() {
        super(new InetSocketAddress((String) configReader.config().get("websocket_hostname"), (Integer) configReader.config().get("websocket_port")));
    }


    /**
     * 触发连接事件
     * 将 WebSocket 赋值给全局变量 wb
     * 将连接状态 ifOpen 设为 True
     * 向服务器后台发送连接信息
     */
    @Override
    public void onOpen(WebSocket conn, ClientHandshake clientHandshake) {
        wb = conn;
        ifOpen = true;
        System.out.println("[MC_QQ]：一个来自：" + conn.getRemoteSocketAddress().getAddress().getHostAddress() + "的新连接。");
    }

    /**
     * 连接断开时触发关闭事件
     * 将连接状态 ifOpen 设为 False
     * 向服务器后台发送断线信息
     */
    @Override
    public void onClose(WebSocket conn, int code, String reason, boolean remote) {
        ifOpen = false;
        System.out.println("[MC_QQ]：连接断开");
    }

    /**
     * 客户端发送消息到服务器时触发事件
     * 向服务器游戏内公屏发送信息
     */
    @Override
    public void onMessage(WebSocket conn, String message) {
    }


    /**
     * 触发异常事件
     * 向服务器后台发送报错信息
     */
    @Override
    public void onError(WebSocket conn, Exception e) {
        if (conn != null) {
            System.out.println("[MC_QQ]：WebSocket 遇到了一些问题。");
        }
    }

    /**
     * 服务启动时触发事件
     * 向后台发送启动信息
     */
    @Override
    public void onStart() {
        System.out.println("[MC_QQ]：WebSockets 服务端已启动");
    }

    /**
     * 定义方法 sendMessage()
     * 将 消息 由服务器发送到 Bot
     */
    void sendMessage(String message) {
        if (websocket.ifOpen) {
            wb.send(message);
        } else {
            System.out.println("[MC_QQ]：连接已断开，无法发送消息");
        }
    }
}
