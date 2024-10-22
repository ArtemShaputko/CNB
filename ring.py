import threading
import time

debug_info = {'data': '', 'updated': False}
mutex = threading.Lock()

def write_debug_info(info):
    global debug_info
    global mutex
    for i in range(0, 100):
        mutex.acquire()
        if not debug_info['updated']:
            debug_info['data'] = info
            debug_info['updated'] = True
            mutex.release()
            break
        mutex.release()
        time.sleep(0.05)