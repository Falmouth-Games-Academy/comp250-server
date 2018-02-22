import threading
import queue

""" A single thread which executes a queue of functions """
class WorkerThread(threading.Thread):
	class QueueItem:
		def __init__(self, callable, args, kwargs):
			self.callable = callable
			self.args = args
			self.kwargs = kwargs
		
		def run(self):
			self.callable(*self.args, **self.kwargs)
			
	def __init__(self):
		self.queue = queue.Queue()
		threading.Thread.__init__(self)
	
	def enqueue(self, callable, *args, **kwargs):
		item = WorkerThread.QueueItem(callable, args, kwargs)
		self.queue.put(item)
	
	def run(self):
		while True:
			item = self.queue.get() # Blocks until an item is available
			try:
				item.run()
			except Exception as e:
				print(e)

