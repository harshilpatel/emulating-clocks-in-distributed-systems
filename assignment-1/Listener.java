import java.io.*;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.*;
import java.util.logging.Logger;

public class Listener extends Thread{
    // listening server for every process
    String name;
    Socket socket;
    ServerSocket server;
    ServerProcess parent;
    Logger logger;

    public static DataInputStream dataInputStream;
    public static DataOutputStream dataOutputStream;


    public Listener(String name, int port, ServerProcess parent) throws IOException{
        this.name = name;
        this.server = new ServerSocket(port);
        this.parent = parent;
        System.out.println("Listener:" + name +  " created");

        logger = Logger.getLogger(name);
    }
    
    @Override
    public void run() {
        super.run();
        System.out.println("Listener:" + name +  " started");
        
        try {
            listen();
        } catch (IOException e){
            
        }
    }
    
    public void listen() throws IOException{
        while(true){
            socket = server.accept();

            // try{Thread.sleep(500);} catch(Exception e){}

            dataInputStream = new DataInputStream(socket.getInputStream());
            dataOutputStream = new DataOutputStream(socket.getOutputStream());
            
            String data = dataInputStream.readUTF();
            
            data = data.replace("{", "");
            data = data.replace("}", "");
            
            // System.out.println(data);

            Map<String,String> mappedData = new HashMap<String, String>();
            String[] splitData = data.split("/*,/*");
            // System.out.println(splitData.length);
            
            for(int i=0; i<splitData.length; i++){
                String[] keyValue = splitData[i].split("/*=/*");
                // System.out.println(keyValue[0]);
                // System.out.println(keyValue[1]);

                mappedData.put(keyValue[0].replace(" ", ""), keyValue[1].replace(" ", ""));
            }

            // System.out.println(mappedData.toString());

            if(mappedData.containsKey("type") && mappedData.get("type").equals("ack")){
                // System.out.println("");
                // ack is received
                int event_id = Integer.valueOf(mappedData.get("event_id"));
                parent.ackEvent(event_id);

            } else if(mappedData.get("type").equals("event")){
                if(!mappedData.containsKey("event_id")){
                    mappedData.put("event_id", "" + this.parent.getQueueLength());
                }

                
                if(mappedData.containsKey("sent_from") && mappedData.get("sent_from").equals(String.valueOf(parent.id))){
                    int event_id = Integer.valueOf(mappedData.get("event_id"));
                    parent.ackEvent(event_id);
                } else {
                    Event e = new Event(mappedData, parent);
                    
                    if(mappedData.containsKey("sent_from")){
                        e.isParentOwner = false;
                    } else {
                        e.isParentOwner = true;
                    }
                    parent.eventQueue.addEventToQueue(e);
                }
                
            }

            socket.close();
        }
    }


    public void addEvent(String data){

    }
}