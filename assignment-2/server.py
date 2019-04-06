import sys, os, socket, logging, math, random, time
from utils import getProcessLogger
from server_process import ServerProcess
from threading import Thread
from multiprocessing import Process
import signal
from constants import *

logger = getProcessLogger('server')
logger.setLevel(LOGGING_LEVEL)

class Server(object):
    def __init__(self, address):
        self.address = address
        self.socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.processes = []
        self.event_counter = 0

    def serve_infinitely(self):
        self.socket_server.bind(self.address)
        self.socket_server.listen(1)

        logger.info("starting server & listen to packets at %s", self.address)

        while True:
            connection, client_address = self.socket_server.accept()
            logger.debug("received a new connection with address %s", client_address)
            try:
                while True:
                    data = connection.recv(BUFF_SIZE)
                    if not data:
                        break

                    logger.debug("received data: %s from client: %s", data, client_address)
                    random_process = random.choice(self.processes)
                    # random_process = self.processes[0]
                    self.event_counter += 1
                    random_process.process_incoming(data, True, self.event_counter)
                    connection.send('')
            finally:
                connection.close()
                logger.debug("closed connection to client with address: %s", client_address)

    def create_child_process(self):
        addresses = [('localhost', random.randint(9000, 9999)) for x in range(NUM_OF_CHILDREN)]
        for i,a in enumerate(addresses):
            logger.info("creating a server process for address: %s", a)
            self.processes.append(ServerProcess(i, a, addresses, 2))
        
        for p in self.processes:
            p.run()


if __name__ == "__main__":
    server = Server(('localhost', 8080))
    server.create_child_process()

    def handle_exit(sig, frame):
        logger.warn("terminating processes")
        for p in server.processes:  
            print "terminating process " + str(p.name)
            p.stop_executing = True
        sys.exit()

    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)
    signal.signal(signal.SIGTSTP, handle_exit)
    signal.signal(signal.SIGQUIT, handle_exit)
    
    server.serve_infinitely()

    # time.sleep(5) 

    # for p in server.processes:
    #     p.join()
    #     p.stop_executing = True
