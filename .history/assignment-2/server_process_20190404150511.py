import os
import sys
import random
import time
import json
from utils import getProcessLogger
from multiprocessing import connection, Process
import threading
from threading import Thread

NUM_OF_CHILDREN = 3
AUTH_KEY = 'djn4lk4'

class BaseEventFeatures(object):
    def __init__(self):
        return

    def print_message(self, msg):
        print msg
        self.logger.debug("print msg %s", msg)

    def add(self, a, b):
        return a+b

    def save_content(self, filename, content):
        self.logger.debug("saving content to file: %s", filename)
        fileobject = open(self.current_owner + " :" + self.filename, 'a')
        fileobject.write(content)
        fileobject.close()


class ServerEvent(BaseEventFeatures):
    def __init__(self, real_owner, current_owner, id, operation_name, *operation_params):
        self.id = id

        self.started = False
        self.finished = False

        self.acknowledged = False

        self.name = "E" + str(self.id)
        self.operation_name = operation_name
        self.operation_params = operation_params
        
        self.real_owner = real_owner
        self.current_owner = current_owner
        self.ack = []

        self.sent_at = 0
        self.recv_at = 0
        self.should_execute_at = 0

        self.logger = getProcessLogger(self.current_owner + ":" + self.name)

        self.logger.info("created event")
    
    def get_normalised_data(self):
        return {
            'type': 'operation',
            'operation_name': self.operation_name,
            'params': self.operation_params,
            'owner': self.real_owner,
            'sender': self.current_owner,
        }
    
    def get_ack(self):
        return {
            'type': 'ack',
            'operation_id': self.id,
        }

    def start_executing(self):
        callable_func = self.get_attr(self, self.operation_name)
        if callable_func:
            callable_func(*self.operation_params)
        return


class ServerProcess(object):
    
    def __init__(self, address, all_address, clock_cycle):
        # super(ServerProcess, self).__init__()

        # self.id = id
        self.address = address

        self.all_address = all_address

        self.started = False
        self.finished = False
        self.events = []
        self.latest_event = ''
        self.threads = []

        self.clock_cycle = clock_cycle
        self.timer = 0

        self.stop_executing = False
        self.logger = getProcessLogger('process')
        self.lock = threading.Lock()



    def ack_event(self, event_id):
        for e in self.events:
            if event_id == e.id:
                e.ack.append(1)
    
    def _run_threads(self):
        self.threads.append(Thread(target = self.serve_events))
        self.threads.append(Thread(target = self.listen_events))
        self.threads.append(Thread(target = self.emulate_clock))

        # start threads
        for t in self.threads:
            t.start()
        
        # wait for the thread
        for t in self.threads:
            t.join()

    def run(self):
        self.name = "P" + str(random.randint(1111,9999))
        self.logger = getProcessLogger(self.name)
        self.logger.info("started process")

        t = Thread(target=self._run_threads)
        t.daemon = True
        t.start()
        
    
    def process_incoming(self, data):
        if type(data) == str:
            data = json.loads(data)

        data_type =  data.get('type')
        if data_type:
            if data_type == 'operation':
                owner = data.get('owner') or self.name
                sender = data.get('sender') or self.name
                name = data.get('operation_name')
                params = data.get('params')
                t = Thread(target=self.add_event, args=(owner, sender, name, params))
                t.start(); t.join()
                # self.add_event(sender, name, params)
            
            if data_type == 'ack':
                event_id = data.get('operation_id')
                self.ack_event(event_id)

            if data_type == 'notify':
                if data.get('msg') == 'destroy':
                    self.stop_executing = True


    def emulate_clock(self):
        while not self.stop_executing:
            time.sleep(self.timer)
            self.timer = self.clock_cycle + self.timer
            self.logger.info("time is %s", self.timer)

    def listen_events(self):
        self.logger.info("started thread listener %s", self.name)
        listener = connection.Listener(self.address, authkey=AUTH_KEY)
        while not self.stop_executing:
            conn = listener.accept()
            self.logger.debug("number of events in thread listener %s", len(self.events))
            if conn:
                self.logger.info("new connection: %s", conn)
                data = conn.recv()
                if data:
                    self.process_incoming(data)
                conn.close()
            
        self.logger.info("stopped listening to events")


    def serve_events(self):
        self.logger.info("started thread server %s", self.name)
        while not self.stop_executing:
            time.sleep(2)
            self.logger.debug("number of events in thread server %s", len(self.events))
            for e in self.events:
                if e.current_owner == self.name and e.ack.count != 3:
                    if not e.sent_at or (e.sent_at and (self.timer - e.sent_at) > 1000):
                        e.sent_at = self.timer
                        for a in self.all_address:
                            conn = connection.Client(a, authkey=AUTH_KEY)
                            conn.send(e.get_normalised_data())
                            conn.close()
                if e.current_owner != self.name and not e.acknowledged:
                    e.acknowledged = True
                    conn = connection.Client(a, authkey=AUTH_KEY)
                    conn.send(e.get_ack())
                    conn.close()
        
        self.logger.info("stopped serving events")


    def add_event(self, real_owner, current_owner, event_name, params):
        # with self.lock:
        new_event = ServerEvent(real_owner, current_owner, random.randint(111, 999), event_name, *params)
        new_event.recv_at = self.timer
        self.latest_event = new_event
        self.events.append(new_event)

    def execute_next_task(self):
        return

    # def serve_indefinitely(self):
    #     while !self.stop_executing:
    #         self.execute_next_task()
    #         time.sleep(self.clock_cycle)

