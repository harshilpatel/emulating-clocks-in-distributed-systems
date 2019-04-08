import java.io.*;
import java.util.*;
import java.util.logging.Logger;

class Event{
    // Event object stores any event. Unique for every process but id remains the same
    
    String name;
    ServerProcess parent;
    
    int id;
    String operationName;
    String operationParams;

    boolean isParentOwner = false;
    
    boolean acknowledgedToOwner = false;
    int acknowledgedBy = 0;

    boolean started = false;
    boolean finished = false;

    boolean sent = false;

    Logger logger = Logger.getLogger("Client");

    public Event(Map data, ServerProcess parent){
        this.id = Integer.parseInt(data.getOrDefault("event_id", "").toString());
        this.name = data.getOrDefault("event_name", "").toString();
        this.operationName = data.getOrDefault("operation_name", "").toString();
        this.operationParams = data.getOrDefault("event_params", "").toString();
        
        this.parent = parent;
        this.logger = Logger.getLogger(this.parent.name + ":" + this.name);

        if(name.equals("")){
            name = "E" + parent.getQueueLength() + 1;
        }

        System.out.println("Event:" + name + " receieved at:" + parent.name);
    }

    String getDetails(){
        Map<String, String> data = new HashMap<String, String>();
        data.put("event_id", Integer.toString(this.id));
        data.put("event_name", this.name);
        data.put("operation_name", this.operationName);
        data.put("event_params", this.operationParams);
        data.put("sent_from", String.valueOf(parent.id));
        data.put("timestamp", "" + parent.timestamp);
        data.put("type", "event");
        
        return data.toString();
    }

    String getAck(){
        Map<String, String> data = new HashMap<String, String>();
        data.put("event_id", Integer.toString(this.id));
        data.put("timestamp", "" + parent.timestamp);
        data.put("type", "ack");

        return data.toString();
    }

    boolean canExecute(){
        if(finished) return false;

        if(isParentOwner && acknowledgedBy >= 3){
            return true;
        }

        if(!isParentOwner && acknowledgedToOwner){
            return true;
        }

        return false;
    }
    
    void beginExecuting(){
        started = true;

        if(isParentOwner){
            System.out.println("Executing: self process:" + name + " at:" + parent.name + " after acknowledgement received from:" + acknowledgedBy + " processes");
        } else {
            System.out.println("Executing: foreign process:" + name + " at:" + parent.name);
        }
        
        finished = true;
    }

    void addAck(){
        if(!finished && acknowledgedBy < 3)
            acknowledgedBy++;
    }

    void acknowledge(){
        acknowledgedToOwner = true;
    }
}