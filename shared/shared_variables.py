from queue import Queue
import threading

# Shared queue for communication between threads
shared_queue_1 = Queue()

# Event to signal threads to stop
shutdown_event_threads = threading.Event()
