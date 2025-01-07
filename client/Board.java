package client;

import java.util.Collections;
import java.util.HashMap;

public class Board {
    private String fen;
    private HashMap<String, String> chessUnicode;
    private String sfondoNero = "\033[48;5;0m";
    private String sfondoBianco = "\033[48;5;8m";

    private void generaUnicode(){
        chessUnicode= new HashMap<String, String>();
        chessUnicode.put("r","♖");
        chessUnicode.put("R","♜");
        chessUnicode.put("p","♙");
        chessUnicode.put("P","♟");
        chessUnicode.put("k","♔");
        chessUnicode.put("K","♚");
        chessUnicode.put("q","♕");
        chessUnicode.put("Q","♛");
        chessUnicode.put("n","♘");
        chessUnicode.put("N","♞");
        chessUnicode.put("b","♗");
        chessUnicode.put("B","♝");
        for (int i = 1; i <= 8; i++){
            chessUnicode.put(Integer.toString(i),String.join("", Collections.nCopies(i, " ")));
        }
        chessUnicode.put("/","\n");
    }

    public Board(){
         generaUnicode();
         fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR";
    }

    public Board(String fen){
        generaUnicode();
        this.fen = fen;
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
                    S+=" ";
                    S+=piece.charAt(j)+" ";
                    colonna++;
                }else{
                    S+=sfondoNero;
                    riga++;
                    colonna = 0;
                    S+="\n";
                }
            }
        }
        return S;
    }
}
