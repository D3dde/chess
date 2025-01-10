package client;

import java.io.*;
import java.net.Socket;
import java.util.Scanner;

public class Client {
    public static void main(String[] args) {
        final String HOST = "127.0.0.1";
        final int PORT = 12345;

        Scanner scanner = new Scanner(System.in);
        Board board = new Board();

        try (
            Socket socket = new Socket(HOST, PORT);
            BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
            PrintWriter out = new PrintWriter(socket.getOutputStream(), true)) {

            String fen = in.readLine();
            board.setFen(fen);

            while (true) {
                System.out.println(board);
                System.out.print("Enter your move (es e2e4): ");
                String move = scanner.nextLine();
                // invia
                out.println(move);
                String response = in.readLine();

                if (response == null) {
                    System.out.println("ERROR");
                    break;
                }
            

                if (response.contains("Invalid move")) {
                    System.out.println(response);
                } else if (response.contains("Game over")) {
                    System.out.println(response);
                    break;
                } else {
                    // riceve
                    fen = response;
                    board = new Board(fen);
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
