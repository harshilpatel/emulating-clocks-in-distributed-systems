from multiprocessing import Process, Queue
from multiprocessing.connection import Listener, Client
from threading import Thread
import time

class P(Process):
    def __init__(self):
        super(P, self).__init__()
        self.name = "ABCD"
    
    def run(self):
        t = Thread(target=self.print_name)
        t.start()
        t.join()

    def print_name(self):
        time.sleep(1)
        print self.name


if __name__ == "__main__":
    pq = []
    q = Queue()
    for i in range(10):
        pq.append(P())
    
    for p in pq:
        p.start()
    
    for p in pq:
        p.join()