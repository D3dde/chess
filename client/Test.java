package client;

import java.util.Scanner;

public class Test{
    public static void main(String[] args){
        Scanner in = new Scanner(System.in);
        Board scacchiera = new Board("rnbqkbnr/pp1ppppp/8/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R");
        System.out.print(scacchiera);
        //System.out.println("inserisci una mossa");
        //String mossa = in.next();
        //manda mossa al server (es e5)
        //se la mossa non è valida riceve lo stesso fen, altrimenti riceve un fen aggiornato contenente sia la mossa che ha fatto il client che quella del pc "server"
        //in questo caso e5 è valida
        //il client controlla se il fen è uguale e li decide cosa fare
        //str = ricevi da server
        //if (scacchiera.equals (str ) : print (mossa non valida etc) else: goto "print(scacchiera)")
    }
}