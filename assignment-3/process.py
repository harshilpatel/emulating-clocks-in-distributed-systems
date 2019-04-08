from utils import getProcessLogger
import threading
import multiprocessing
import time

logger = getProcessLogger("process")

class Lock(object):
    def __init__(self):
        self.lock = False
    
    def acquire(self):
        while self.lock:
            pass

        self.lock = True
        return 
    
    def release(self):
        self.lock = False

lock = Lock()

class FileHandler(threading.Thread):
    lock = threading.Lock()

    def __init__(self, name, filename):
        threading.Thread.__init__(self)
        self.name = name
        self.filename = filename
        self.logger = getProcessLogger(self.name)
    
    def run(self):
        self.beginCenter()
    

    def beginCenter(self):
        for i in range(10):
            time.sleep(1)
            self.logger.debug("Requesting lock")

            lock.acquire()

            self.logger.debug("lock acquired: writing to file")
            
            output_file = open(self.filename, 'a')
            output_file.write("%s - %s\n" % (self.name, i))
            output_file.close()

            self.logger.debug("closing file")
            self.logger.debug("Releasing lock")
            
            lock.release()