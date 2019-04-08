import java.io.*;
import java.util.*;
import java.util.logging.Logger;

public class ServerProcess extends Thread{
    // Instance of the Server process {rename it later}
    int id;
    String name;
    Listener listener;
    Sender sender;
    // List<Event> events = new ArrayList<Event>();
    ProcessQueue eventQueue;
    Logger logger;

    int port;

    public ServerProcess(int id, String name, int port) throws IOException{
        this.id = id;
        this.name = name;
        this.port = port;
        
        listener = new Listener(name + ":Listener", port, this);
        sender = new Sender(name + ":Sender", this);

        eventQueue = new ProcessQueue(this);

        
        logger = Logger.getLogger("P" + name);
        System.out.println(name + " created");
    }
    
    int getQueueLength(){
        return eventQueue.events.size();
    }
    
    void ackEvent(int event_id){
        Iterator<Event> it = eventQueue.events.iterator();
            while(it.hasNext()){
                Event e = it.next();
                if(e.id == event_id)
                    e.addAck();   
            }
    }
    
    @Override
    public void run() {
        super.run();
        
        listener.start();
        sender.start();
        startExecuter();
        
        System.out.println("Process:" + name +  " started");
    }
    
    
    void startExecuter(){
        new Thread(){
            public void run(){
                while(true){
                    try{ Thread.sleep(2000);}catch(Exception e){}
                    eventQueue.executeNextEvent();
                }
            }
        }.start();
    }


}