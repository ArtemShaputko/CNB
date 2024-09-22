from tkinter import *
from tkinter import ttk

def bin_to_str(data):
    res = ''
    for i in data:
        if i == 0:
            res += '0'
        else:
            res += chr(i)
    return res


class StatusWindow:
    def __init__(self, context, port):
        self.port = port
        self.context = context

        self.statusFrame = ttk.Frame(context.root, borderwidth=1, relief=SOLID, padding=[10, 10])
        self.statusFrame.grid(row=1, column=0, sticky="nsew")

        status_name = ttk.Label(self.statusFrame, text="Status")
        status_name.place(relx=0.5, anchor=CENTER)
        self.status_text = Label(self.statusFrame, text="", height=2)
        self.status_text.place(relwidth=1, relheight=0.2, rely=0.1)
        self.update_port_info(0)
        self.packet = Text(self.statusFrame, state=DISABLED, bg="#FFFFFF")
        self.packet.place(relwidth=1, relheight=0.7, rely=0.3)

    def update_port_info(self, bytes_sent):
        self.status_text.config(text=f"Port Baudrate: {self.port.baudrate} "
                                     f"baud\nBytes sent: {bytes_sent}")

    def show_packets(self, data, changes):
        self.packet.config(state=NORMAL)
        self.packet.insert(END, bin_to_str(data) + '\n')
        end_index = self.packet.index("end-1c")
        line_number = int(end_index.split(".")[0]) - 1
        for i in changes:
            self.packet.tag_add("highlight",f"{line_number}.{i+10}", f"{line_number}.{i+14}" )
        self.packet.tag_config("highlight", foreground="red")

        self.packet.config(state=DISABLED)
        self.packet.yview(END)

