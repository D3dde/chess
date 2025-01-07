package client;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.Socket;

public class Client {
    public static void main(String[] args) {
        String host = "127.0.0.1"; // Server address
        int port = 12345; // Server port

        try (
            
            Socket socket = new Socket(host, port);
            PrintWriter out = new PrintWriter(socket.getOutputStream(), true);
            BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()))) {

            // Read the message from the server
            String message = in.readLine();
            System.out.println("Received from server: " + message);

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
