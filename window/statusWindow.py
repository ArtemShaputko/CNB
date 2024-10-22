from tkinter import *
from tkinter import ttk

class StatusWindow:
    def __init__(self, context, port):
        self.port = port
        self.context = context

        self.statusFrame = ttk.Frame(context.root, borderwidth=1, relief=SOLID, padding=[10, 10])
        self.statusFrame.grid(row=1, column=0, sticky="nsew")

        status_name = ttk.Label(self.statusFrame, text="Status")
        status_name.place(relx=0.5, anchor=CENTER)
        self.status_text = Label(self.statusFrame, text="", height=2)
        self.status_text.place(relwidth=1, relheight=0.1, rely=0.05)
        self.update_port_info(0)
        self.packet = Text(self.statusFrame, state=DISABLED, bg="#FFFFFF")
        self.packet.place(relwidth=1, relheight=0.9, rely=0.15)

    def update_port_info(self, bytes_sent):
        self.status_text.config(text=f"Port Baudrate: {self.port.baudrate} "
                                     f"baud | Bytes sent: {bytes_sent}")

    def show_packets(self, data: bytes, changes, error_pos : int = None):
        self.packet.config(state=NORMAL)
        self.packet.insert(END, data.hex() + '\n')
        end_index = self.packet.index("end-1c")
        line_number = int(end_index.split(".")[0]) - 1
        for i in changes:
            self.packet.tag_add("staff",f"{line_number}.{2*i+12}", f"{line_number}.{2*i+20}" )
        self.packet.tag_add("FCS", f"{line_number}.68", f"{line_number}.70")
        if error_pos is not None:
            self.packet.tag_add("Error", f"{line_number}.{int((29*8 - error_pos - 1)/4) + 12}")
        self.packet.tag_config("staff", foreground="blue")
        self.packet.tag_config("FCS", foreground="green")
        self.packet.tag_config("Error", foreground="red")
        self.packet.config(state=DISABLED)
        self.packet.yview(END)

