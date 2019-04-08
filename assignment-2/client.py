import sys, os, socket, logging, math
import json
from utils import getProcessLogger
import time
from constants import *


logger = getProcessLogger('Client')
logger.setLevel(LOGGING_LEVEL)

address = ('localhost', 8080)

message_counter = 0


while message_counter < 10:
    message_counter += 1
    content = "message %s" % message_counter 
    
    msg = {
        'type': 'operation',
        'operation_name': "save_content",
        'params': ["eventOutput.txt", content],
    }
    
    time.sleep(0.8)
    try:
        socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_client.connect(address)
        socket_client.send(json.dumps(msg))
        logger.info("Sent message")
    except Exception as e:
        logger.info("Error")
        pass
    
    socket_client.close()

# print socket_client.sendto(json.dumps(msg),address)