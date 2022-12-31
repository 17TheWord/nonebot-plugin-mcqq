package com.scareye.mcqq;

import java.net.URI;
import java.net.URISyntaxException;

import org.java_websocket.client.WebSocketClient;
import org.java_websocket.handshake.ServerHandshake;

import static com.scareye.mcqq.MC_QQ.instance;
import static com.scareye.mcqq.MC_QQ.wsClient;
import static com.scareye.mcqq.MC_QQ.say;

public class WSClient extends WebSocketClient {

    public WSClient() throws URISyntaxException {
        super(new URI("ws://" + ConfigReader.getAddress() + ":" + ConfigReader.getPort()));
    }

    @Override
    public void onOpen(ServerHandshake serverHandshake) {
        sendMessage("{\"server_name\": \"" + ConfigReader.getServerName() + "\", \"event_name\": \"ConnectEvent\", \"status\": \"" + wsClient.isOpen() + "\"}");
        say("[MC_QQ]：已成功连接 WebSocket 服务器。");
    }

    /**
     * 收到消息时触发
     * 向服务器游戏内公屏发送信息
     */
    @Override
    public void onMessage(String message) {
        instance.getServer().spigot().broadcast(Utils.processJsonMessage(message));
    }

    @Override
    public void onClose(int i, String s, boolean b) {
        if (wsClient != null) {
            wsClient.sendPing();
        }
    }

    @Override
    public void onError(Exception exception) {
        if (wsClient != null) {
            try {
                wsClient = new WSClient();
                while (!wsClient.isOpen()) {
                    Thread.sleep(3000);
                    say("[MC_QQ]：WebSocket 连接已断开,正在重新连接。");
                    wsClient.connectBlocking();
                    if (wsClient.isOpen()) {
                        break;
                    }
                }
            } catch (URISyntaxException | InterruptedException e) {
                e.printStackTrace();
            }
        }
    }

    public void sendMessage(String message) {
        if (wsClient.isOpen()) {
            wsClient.send(message);
        } else {
            say("[MC_QQ]：发送消息失败，没有连接到 WebSocket 服务器。");
        }
    }
}
