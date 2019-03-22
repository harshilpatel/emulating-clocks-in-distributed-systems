import os, sys, random
from utils import getProcessLogger

class BaseEventTypes(object):
    def __init__(self, filename):
        return
    
    def add(self, a, b):
        return a+b

    def save_content(self, content):
        fileobject = open(self.filename, 'a')
        fileobject.write(content)
        fileobject.close()

class Event(object, BaseEventTypes):
    def __init__(self, id, operation_name, operation_params, filename, parent):
        self.id = id

        self.started = False
        self.finished = False
        
        self.name = "E" + str(self.id)
        self.operation_name = operation_name
        self.filename = filename
        self.parent = parent

        self.logger = getProcessLogger(parent.name + ":" + name)
    
    def start_executing(self):
        callable_func = self.get_attr(self, self.operation_name)
        if callable_func:
            callable_func(self.operation_params)
        
        return

class ServerProcess(object):
    def __init__(self, id, filename):
        self.id = id
        self.started = False
        self.finished = False
        self.tasks = []

        self.name = "P" + str(self.id)
        self.filename = filename
        self.logger = getProcessLogger(name)

    def add_event(self, event_name, *params):
        self.tasks.add(Event(len(self.tasks) + 1, event_name, **params, self.filename, self))