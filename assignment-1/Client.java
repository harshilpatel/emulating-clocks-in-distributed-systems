import java.io.*;
import java.net.Socket;
import java.util.*;
import java.util.logging.Logger;

public class Client{
    // base client sending some request

    public static Socket socket;
    public static DataInputStream dataInputStream;
    public static DataOutputStream dataOutputStream;
    public static Logger logger = Logger.getLogger("Client");

    public static void main(String[] args) throws IOException{
        System.out.println("starting client");

        int[] ports= new int[]{9000, 9001, 9002};
        int count = 0;
        while(count < 2){
            
            socket = new Socket("localhost", ports[count]);
            dataInputStream = new DataInputStream(System.in);
            dataOutputStream = new DataOutputStream(socket.getOutputStream());
            Map<String, String> data = new HashMap<String, String>();
            data.put("operation_name", "print");
            data.put("event_params", "HelloWorld!");
            data.put("type", "event");
            data.put("event_name", "E" + (count + 1));
            
            dataOutputStream.writeUTF(data.toString());
            socket.close();
            
            count++;
        }
    }
}