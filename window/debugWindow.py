import threading
import time
from tkinter import *

import ring


class DebugWindow:
    def __init__(self):
        root = Tk()
        root.geometry('500x500')
        root.title('Monitor Window')
        self.text = Text(root, state=DISABLED, bg="#E6E6FA")
        self.text.pack(side=TOP, fill=BOTH, expand=True, padx=10, pady=10)
        threading.Thread(target=self.check, daemon=True).start()
        root.mainloop()

    def check(self):
        while True:
            ring.mutex.acquire()
            if ring.debug_info['updated']:
                self.text.config(state=NORMAL)
                self.text.insert(END, ring.debug_info['data'])
                self.text.insert(END, '\n')
                self.text.config(state=DISABLED)
                self.text.yview(END)
                ring.debug_info['updated'] = False
            ring.mutex.release()
            time.sleep(0.1)