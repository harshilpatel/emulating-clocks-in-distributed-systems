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

            Map<String,String> mappedData = new HashMap<String, String>();
            String[] splitData = data.split("/*,/*");
            
            for(int i=0; i<splitData.length; i++){
                String[] keyValue = splitData[i].split("/*=/*");

                mappedData.put(keyValue[0].replace(" ", ""), keyValue[1].replace(" ", ""));
            }

            

            if(mappedData.containsKey("type") && mappedData.get("type").equals("ack")){
                // ack is received
                int event_id = Integer.valueOf(mappedData.get("event_id"));
                parent.ackEvent(event_id);

            } else if(mappedData.get("type").equals("event")){
                // event is received
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

                    if(mappedData.containsKey("timestamp")){
                        int ts = Integer.parseInt(mappedData.get("timestamp"));
                        while(ts > parent.timestamp){
                            parent.timestamp = parent.timestamp + parent.proceesorSpeed;
                        }

                        System.out.println("Processor ts was incremented to:" + parent.timestamp);
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