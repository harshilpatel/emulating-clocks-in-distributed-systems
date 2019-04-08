import java.io.*;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.*;


class ProcessQueue{
    List<Event> events = new ArrayList<Event>();

    public ProcessQueue(ServerProcess parent){

    }

    void addEventToQueue(Event event){
        events.add(event);
    }

    void executeNextEvent(){
        Iterator<Event> it = events.iterator();
        while(it.hasNext()){
            Event e = it.next();
            if(e.finished){
                continue;
            }
            
            if(e.canExecute()){
                e.beginExecuting();
                break;
            }

        }
    }

    void acknowledgeEvent(int event_id){
        Iterator<Event> it = events.iterator();
        while(it.hasNext()){
            Event e = it.next();
            if(e.id == event_id){
                e.acknowledge();
            }

        }
    }
}