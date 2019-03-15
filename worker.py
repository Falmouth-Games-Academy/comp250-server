import threading
import queue
from enum import Enum

class WorkerItemStatus(Enum):
    waiting = 1
    running = 2
    finished = 3

class WorkerThread(threading.Thread):
    """ A single thread which executes a queue of functions """

    class QueueItem:
        def __init__(self, callable, args, kwargs):
            self.callable = callable
            self.args = args
            self.kwargs = kwargs
            self.status = WorkerItemStatus.waiting
        
        def run(self):
            self.status = WorkerItemStatus.running
            try:
                self.callable(*self.args, **self.kwargs)
            except Exception as e:
                print(e)
            finally:
                self.status = WorkerItemStatus.finished
        
    def __init__(self):
        self.queue = queue.Queue()
        threading.Thread.__init__(self)
    
    def enqueue(self, callable, *args, **kwargs):
        item = WorkerThread.QueueItem(callable, args, kwargs)
        self.queue.put(item)
        return item
    
    def run(self):
        while True:
            item = self.queue.get() # Blocks until an item is available
            item.run()

