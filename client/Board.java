package client;

import java.util.Collections;
import java.util.HashMap;

public class Board {
    private String fen;
    private HashMap<String, String> chessUnicode;
    private String sfondoNero = "\033[48;5;0m";
    private String sfondoBianco = "\033[48;5;8m";

    private void genUnicode(){
        chessUnicode = new HashMap<>();
        chessUnicode.put("r", "♖");
        chessUnicode.put("R", "♜");
        chessUnicode.put("p", "♙");
        chessUnicode.put("P", "♟");
        chessUnicode.put("k", "♔");
        chessUnicode.put("K", "♚");
        chessUnicode.put("q", "♕");
        chessUnicode.put("Q", "♛");
        chessUnicode.put("n", "♘");
        chessUnicode.put("N", "♞");
        chessUnicode.put("b", "♗");
        chessUnicode.put("B", "♝");
        
        for (int i = 1; i <= 8; i++) {
            chessUnicode.put(Integer.toString(i), String.join("", Collections.nCopies(i, " ")));
        }
        
        chessUnicode.put("/", "\n");
    }

    public Board(){
         genUnicode();
         fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR";
    }

    public Board(String fen){
        genUnicode();
        this.fen = removeUselessInfo(fen);
    }

    private String removeUselessInfo(String fen) {
        return fen.split(" ")[0];
    }

    public String toString(){
        String S = "";
        int riga = 0;
        int colonna = 0;
        for (int i = 0; i<fen.length(); i++){
            String piece = chessUnicode.get(""+fen.charAt(i));

            for (int j = 0; j<piece.length() ; j++){

                // colore sfondo
                if ((riga  + colonna) % 2 == 0){
                    S+=sfondoNero;
                }else{
                    S+=sfondoBianco;
                }

                // piazza il pezzo
                if (piece.charAt(j)!='\n'){
                    S+=" "+piece.charAt(j)+" ";
                    colonna++;
                }else{
                    riga++;
                    colonna = 0;
                    S+="\033[49m\n"; //backround trasparente + a capo
                }
            }
        }
        S+="\033[49m";
        return S;
    }

    public void setFen(String fen){
        this.fen = removeUselessInfo(fen);
    }
}
