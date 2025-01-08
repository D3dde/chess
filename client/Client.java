package client;

import java.io.*;
import java.net.Socket;
import java.util.Scanner;

public class Client {
    public static void main(String[] args) {
        final String HOST = "127.0.0.1";
        final int PORT = 65432;

        try (Socket socket = new Socket(HOST, PORT);
            BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
            PrintWriter out = new PrintWriter(socket.getOutputStream(), true)) {

            Scanner scanner = new Scanner(System.in);
            String fen = in.readLine();
            Board board = new Board(fen);

            while (true) {
                System.out.println(board);
                System.out.print("Enter your move (e.g., e2e4): ");
                String move = scanner.nextLine();

                out.println(move);
                String response = in.readLine();

                if (response.contains("Invalid move")) {
                    System.out.println(response);
                } else if (response.contains("Game over")) {
                    System.out.println(response);
                    break;
                } else {
                    fen = response;
                    board = new Board(fen);
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
