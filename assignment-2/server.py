import sys, os, socket, logging, math, random, time
from utils import getProcessLogger
from server_process import ServerProcess
from threading import Thread
from multiprocessing import Process
import signal

logger = getProcessLogger('server')
NUM_OF_CHILDREN = 3
BUFF_SIZE = 1024

class Server(object):
    def __init__(self, address):
        self.address = address
        self.socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.processes = []

    def serve_infinitely(self):
        self.socket_server.bind(self.address)
        self.socket_server.listen(1)

        logger.info("starting server & listen to packets at %s", self.address)


        while True:
            connection, client_address = self.socket_server.accept()
            logger.info("received a new connection with address %s", client_address)
            try:
                while True:
                    data = connection.recv(BUFF_SIZE)
                    if not data:
                        break

                    logger.debug("received data: %s from client: %s", data, client_address)
                    # result = self.process_request_data(data)
                    connection.send('')
            finally:
                connection.close()
                logger.info("closed connection to client with address: %s", client_address)
    
    def create_child_process(self):
        addresses = [('localhost', random.randint(9000, 9999)) for x in range(NUM_OF_CHILDREN)]
        for a in addresses:
            logger.info("creating a server process for address: %s", a)
            self.processes.append(ServerProcess(a, addresses, 10))
        
        for p in self.processes:
            p.start()




if __name__ == "__main__":
    server = Server(('localhost', 8080))

    def handle_exit(sig, frame):
        logger.warn("terminating processes")
        for p in server.processes:
            p.stop_executing = True
            p.terminate()
        sys.exit()

    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)
    
    server.create_child_process()
    server.serve_infinitely()

    # time.sleep(5) 

    # for p in server.processes:
    #     p.join()
    #     p.stop_executing = True
