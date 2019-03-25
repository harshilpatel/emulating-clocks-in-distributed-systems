import os
import sys
import random
import time
from utils import getProcessLogger
from multiprocessing import connection, Process
from threading import Thread

NUM_OF_CHILDREN = 3
AUTH_KEY = 'djn4lk4'

class BaseEventFeatures(object):
    def __init__(self):
        return

    def print_message(self, msg):
        print msg

    def add(self, a, b):
        return a+b

    def save_content(self, filename, content):
        fileobject = open(self.parent + ":" + self.filename, 'a')
        fileobject.write(content)
        fileobject.close()


class ServerEvent(BaseEventFeatures):
    def __init__(self, parent, id, operation_name, *operation_params):
        self.id = id

        self.started = False
        self.finished = False

        self.name = "E" + str(self.id)
        self.operation_name = operation_name
        self.operation_params = operation_params
        
        self.parent = parent
        self.ack = []

        self.sent_at = 0
        self.recv_at = 0
        self.should_execute_at = 0

        self.logger = getProcessLogger(parent + ":" + name)

        self.logger.info("created event")
    
    def get_normalised_data(self):
        return {
            'type': 'operaton',
            'operation_name': self.operation_name,
            'params': self.operation_params,
            'owner': self.parent
        }

    def start_executing(self):
        callable_func = self.get_attr(self, self.operation_name)
        if callable_func:
            callable_func(*self.operation_params)
        return


class ServerProcess(Process):
    def __init__(self, address, all_address, clock_cycle):
        super(ServerProcess, self).__init__()

        # self.id = id
        self.address = address

        self.all_address = all_address

        self.started = False
        self.finished = False
        self.events = []
        self.threads = []

        self.clock_cycle = clock_cycle
        self.timer = 0

        self.stop_executing = False

    def ack_event(self, event_id):
        for e in self.events:
            if event_id == e.id:
                e.ack.append(1)
    
    def run(self):
        self.name = "P" + str(self.pid)
        self.logger = getProcessLogger(self.name)
        self.logger.info("started process")

        self.threads.append(Thread(target = self.listen_events))
        self.threads.append(Thread(target = self.serve_events))

        # start threads
        for t in self.threads:
            t.start()
        
        # wait for the thread
        for t in self.threads:
            t.join()

    
    def process_incoming(self, data):
        data_type =  data.get('type')
        if data_type:
            if data_type == 'operation':
                sender = data.get('sender')
                name = data.get('operation_name')
                params = data.get('params')
                self.add_event(sender, name, params)
            
            if data_type == 'ack':
                event_id = data.get('operation_id')
                self.ack_event(event_id)

            if data_type == 'notify':
                if data.get('msg') == 'destroy':
                    self.stop_executing = True


    def emulate_clock(self):
        while not self.stop_executing:
            self.timer = self.clock_cycle + self.timer

    def listen_events(self):
        self.logger.info("started thread listener")
        listener = connection.Listener(self.address, authkey=AUTH_KEY)
        while not self.stop_executing:
            conn = listener.accept()
            if conn:
                self.logger.info("new connection: %s", conn)
                data = conn.recv()
                if data:
                    self.process_incoming(data)
                conn.close()
        
        self.logger.info("stopped listening to events")


    def serve_events(self):
        self.logger.info("started thread server")

        while not self.stop_executing:
            for e in self.events:
                if e.parent == self.name and e.ack.count != 3:
                    for a in self.all_address:
                        conn = connection.Client(a, authkey=AUTH_KEY)
                        conn.send(e.get_normalised_data())
                        conn.close()
        
        self.logger.info("stopped serving events")


    def add_event(self, owner, event_name, params):
        self.events.add(ServerEvent(owner, random.randint(111, 999), event_name, *params))

    def execute_next_task(self):
        return

    # def serve_indefinitely(self):
    #     while !self.stop_executing:
    #         self.execute_next_task()
    #         time.sleep(self.clock_cycle)

