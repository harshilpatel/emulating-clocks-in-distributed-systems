import java.io.*;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.*;
import java.util.logging.*;

public class Sender extends Thread{
    // sender server for every process that emits any newly created event by the server

    String name;
    int ports[];
    ServerProcess parent;
    Logger logger;

    public Sender(String name, ServerProcess parent){
        this.name = name;
        this.parent = parent;
        ports = new int[]{9000, 9001, 9002};
        System.out.println("Sender:" + name +  " created");

        logger = Logger.getLogger(name);
    }
    
    @Override
    public void run(){
        super.run();   
        System.out.println("Sender:" + name +  " started");

        try{
            beginSender();
        } catch(IOException e){

        }
    }

    public void beginSender() throws IOException{
        while(true){
            try{Thread.sleep(2000);} catch(Exception e){}

            Iterator<Event> it = parent.eventQueue.events.iterator();
            while(it.hasNext()){
                Event e = it.next();

                if(e.finished)
                    continue;
    
                if(!e.isParentOwner && !e.acknowledgedToOwner && !e.sent){
                    parent.eventQueue.acknowledgeEvent(e.id);
                    acknowledgeEvent(e);
                } else if(e.isParentOwner && e.acknowledgedBy == 0){
                    transmitEvent(e);
                }
            }
        }
    }

    void transmitEvent(Event e) throws IOException{
        for (int i =0; i < ports.length; i++) {
            int p = ports[i];

            Socket socket = new Socket("localhost", p);
            DataOutputStream out = new DataOutputStream(socket.getOutputStream());
            out.writeUTF(e.getDetails());
            socket.close();
        }
    }

    public void acknowledgeEvent(Event e) throws IOException{
        for (int i = 0; i < ports.length; i++) {
            int p = ports[i];
            Socket socket = new Socket("localhost", p);
            DataOutputStream out = new DataOutputStream(socket.getOutputStream());
            out.writeUTF(e.getAck());
            socket.close();
        }
    }
}