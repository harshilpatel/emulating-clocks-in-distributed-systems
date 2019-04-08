import java.io.*;
import java.util.*;


public class Server{
    // Base Server starting connections

    public static void main(String[] args) throws IOException{
        ServerProcess p1 = new ServerProcess(1, "P1", 9000);
        ServerProcess p2 = new ServerProcess(2, "P2", 9001);
        ServerProcess p3 = new ServerProcess(3, "P3", 9002);

        // p1.setDaemon(true);
        // p2.setDaemon(true);
        // p3.setDaemon(true);


        p1.start();
        p2.start();
        p3.start();
    }
}