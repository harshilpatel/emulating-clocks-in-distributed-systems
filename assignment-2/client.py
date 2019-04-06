import sys, os, socket, logging, math
import json
from utils import getProcessLogger
import time



logger = getProcessLogger('client')

address = ('localhost', 8080)

msg = {
    'type': 'operation',
    'operation_name': "print_message",
    'params': ("abc"),
}


while True:
    time.sleep(5)
    try:
        socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_client.connect(address)
        socket_client.send(json.dumps(msg))
        socket_client.close()
        print "sent"
    except:
        print "error"
        pass

# print socket_client.sendto(json.dumps(msg),address)