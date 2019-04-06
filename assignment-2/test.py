from multiprocessing import Process, Queue
from multiprocessing.connection import Listener, Client
from threading import Thread
import time

class P(Process):
    def __init__(self):
        super(P, self).__init__()
        self.list_of_items = []
        # self.name = "ABCD"
    
    def run(self):
        for i in range(2):
            t = Thread(target=self.add_names)
            t.start()
            t.join()
        
            t = Thread(target=self.print_names)
            t.start()
            t.join()

    def print_names(self):
        print self.list_of_items

    def add_names(self):
        # time.sleep(1)
        self.list_of_items.append("new name")


if __name__ == "__main__":
    pq = []
    q = Queue()
    # for i in range(10):
    pq.append(P())
    
    for p in pq:
        p.start()
    
    for p in pq:
        p.join()