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
        self.status_label = Label(self.statusFrame, text="", height=10, background="#FFFFFF")
        self.status_label.place(relwidth=1, relheight=0.9, rely=0.1)
        self.update_port_info(0)

    def update_port_info(self, bytes_sent):
        self.status_label.config(text=f"Скорость порта: {self.port.baudrate} бод\nКоличество переданных байт: {bytes_sent}")