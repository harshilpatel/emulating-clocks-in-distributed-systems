from utils import getProcessLogger
from process import FileHandler

logger = getProcessLogger("server")

FILENAME = "result.txt"

out_file = open(FILENAME, 'w')
out_file.close()

if __name__ == "__main__":
    processes = [] 
    for i in range(10):
        processes.append(FileHandler("P" + str(i) , FILENAME))

    for p in processes:
        p.start()
    
    for p in processes:
        p.join()