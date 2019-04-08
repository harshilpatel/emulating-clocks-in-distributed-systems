import os
import sys
import random
import time
import json
from utils import getProcessLogger
from multiprocessing import connection, Process
import threading
from threading import Thread
from constants import *

class BaseEventFeatures(object):
    def __init__(self):
        return

    def print_message(self, msg):
        self.logger.info("print_message: %s", msg)

    def add(self, a, b):
        return a+b

    def save_content(self, filename, content):
        content = "\n" + content
        self.logger.info("saving content to file: %s", filename)
        fileobject = open(self.parent.name + ":" + filename, 'a')
        fileobject.write(content)
        fileobject.close()

class ExecutionQueue(object):
    def __init__(self, parent, process_index):
        self.queue = {}
        self.parent = parent
        self.current_time_stamp = [0 for x in range(NUM_OF_CHILDREN)]
        self.last_executed_stamp = [[0 for x in range(NUM_OF_CHILDREN)]]
        self.process_index = process_index

        self.logger = getProcessLogger(self.parent.name + ": ExecutionQueue")
        self.logger.setLevel(LOGGING_LEVEL)
    
    def execute_next_event(self):
        for e in sorted(self.queue.keys()):
            event = self.queue[e]
            if not event.started and not event.finished:
                event.start_executing()
    
    def add_event_to_queue(self, event):
        self.set_time_stamp(event.timestamp)
        event.timestamp = self.current_time_stamp
        self.queue[event.get_time_stamp()] = event

        self.logger.debug("adding event:%s to queue", event.name)
    
    def get_next_timestamp(self):
        return [j+1 if i == self.parent.id else j for i,j in enumerate(self.current_time_stamp)]

    def get_time_stamp(self):
        return ''.join([str(x) for x in self.current_time_stamp])
    
    def set_time_stamp(self, timestamp):
        self.current_time_stamp = [max(j, self.current_time_stamp[i]) for i,j in enumerate(timestamp)]

class ServerEvent(BaseEventFeatures):
    def __init__(self, parent, is_real_owner, id, operation_name, operation_params):
        self.id = id

        self.started = False
        self.finished = False

        self.acknowledged = False

        self.name = "E" + str(self.id)
        self.operation_name = operation_name
        self.operation_params = operation_params
        
        self.parent = parent
        self.is_real_owner = is_real_owner
        self.ack = []

        self.sent_at = 0
        self.recv_at = 0
        self.should_execute_at = 0

        self.timestamp = [0 for x in range(NUM_OF_CHILDREN)]

        self.logger = getProcessLogger(self.parent.name + ":" + self.name)
        self.logger.setLevel(LOGGING_LEVEL)

        self.logger.info("created event:%s", self.name)
    
    def get_time_stamp(self):
        return ''.join([str(x) for x in self.timestamp])
    
    def get_normalised_data(self):
        return {
            'type': 'operation',
            'operation_name': self.operation_name,
            'params': self.operation_params,
            'is_real_owner': self.is_real_owner,
            'timestamp' : self.timestamp,
            'id': self.id,
            'sender': self.parent.name,
        }
    
    def get_ack(self):
        return {
            'type': 'ack',
            'operation_id': self.id,
        }

    def start_executing(self):
        self.started = True
        self.logger.info("executing %s:%-10s when ts(%s):%-10s", self.name, self.timestamp, self.parent.name, self.parent.execution_queue.current_time_stamp)
        self.finished = True
        callable_func = getattr(self, self.operation_name)
        if callable_func:
            callable_func(*self.operation_params)
        return None
    
        
    @property
    def can_be_executed(self):
        return False

class ServerProcess(object):
    def __init__(self, id, address, all_address, clock_cycle):
        # id is 0 indexed

        self.id = id
        self.name = "P" + str(id)
        self.address = address

        self.all_address = all_address

        self.execution_queue = ExecutionQueue(self, id)

        self.started = False
        self.finished = False
        self.events = []
        self.latest_event = ''
        self.threads = []

        self.clock_cycle = clock_cycle
        self.timer = 0

        self.stop_executing = False
        self.logger = getProcessLogger('process')
        self.logger.setLevel(LOGGING_LEVEL)
        self.lock = threading.Lock()



    def ack_event(self, event_id):
        for e in self.events:
            if event_id == e.id:
                e.ack.append(1)
    
    def _run_threads(self):
        self.threads.append(Thread(target = self.serve_events))
        self.threads.append(Thread(target = self.listen_events))
        self.threads.append(Thread(target = self.execute_events))
        self.threads.append(Thread(target = self.emulate_clock))

        # start threads
        for t in self.threads:
            t.start()
        
        # wait for the thread
        for t in self.threads:
            t.join()

    def run(self):
        self.logger = getProcessLogger(self.name)
        self.logger.setLevel(LOGGING_LEVEL)
        self.logger.info("started process")

        t = Thread(target=self._run_threads)
        t.daemon = True
        t.start()
        
    
    def process_incoming(self, data, set_owner = False, event_counter = 0):
        if type(data) == str:
            data = json.loads(data)

        data_type =  data.get('type')
        if data_type:
            if data_type == 'operation':
                data['is_real_owner'] = set_owner
                if set_owner:
                    data['id'] = event_counter
                    # data['id'] = self.execution_queue.current_time_stamp[self.id] + 1

                self.create_event(data)
                self.logger.info("-"*30 + " changed time stamp: %s", self.execution_queue.current_time_stamp)
            
            # if data_type == 'ack':
            #     event_id = data.get('operation_id')
            #     self.ack_event(event_id)

            # if data_type == 'notify':
            #     if data.get('msg') == 'destroy':
            #         self.stop_executing = True


    def emulate_clock(self):
        while not self.stop_executing:
            time.sleep(self.timer)
            self.timer = self.clock_cycle + self.timer
            # self.logger.info("time is %s", self.timer)

    def listen_events(self):
        self.logger.info("started thread listener %s", self.name)
        listener = connection.Listener(self.address, authkey=AUTH_KEY)
        while not self.stop_executing:
            conn = listener.accept()
            if conn:
                data = conn.recv()
                self.logger.debug("received new event: %s", "E" + str(data.get('id') or 0))
                if data:
                    self.process_incoming(data)
                conn.close()
            
        self.logger.info("stopped listening to events")


    def serve_events(self):
        self.logger.info("started thread server %s", self.name)
        while not self.stop_executing:
            # time.sleep(3)
            for e in self.events:
                # if not e.is_real_owner:
                #     if not e.sent_at or (e.sent_at and (self.timer - e.sent_at) > 1000):
                #         e.sent_at = self.timer
                #         for a in self.all_address:
                #             conn = connection.Client(a, authkey=AUTH_KEY)
                #             conn.send(e.get_normalised_data())
                #             conn.close()
                if e.is_real_owner and not e.sent_at:
                    # e.acknowledged = True
                    e.sent_at = self.timer
                    for i,a in enumerate(self.all_address):
                        if i == self.id:
                            continue
                            
                        conn = connection.Client(a, authkey=AUTH_KEY)
                        conn.send(e.get_normalised_data())
                        conn.close()
        
        self.logger.info("stopped serving events")
    
    def execute_events(self):
        while not self.stop_executing:
            time.sleep(3)
            self.execution_queue.execute_next_event()

    def create_event(self, data):
        # creates a new events and adds it to the pool

        is_real_owner = data.get('is_real_owner')
        event_name = data.get('operation_name')
        params = data.get('params')
        timestamp = data.get('timestamp')
        event_id = data.get('id') or 0

        new_event = ServerEvent(self, is_real_owner, event_id, event_name, params)
        
        if is_real_owner:
            new_event.timestamp = self.execution_queue.get_next_timestamp()
            self.execution_queue.current_time_stamp = new_event.timestamp
        
        if timestamp:
            self.execution_queue.set_time_stamp(timestamp)
            new_event.timestamp = self.execution_queue.current_time_stamp
        
        new_event.recv_at = self.timer
        self.latest_event = new_event
        
        
        self.events.append(new_event)
        self.execution_queue.add_event_to_queue(new_event)

        return new_event
