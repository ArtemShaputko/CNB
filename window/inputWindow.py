from tkinter import *
from tkinter import ttk


class InputWindow:
    def __init__(self, context):
        self.context = context
        inputFrame = ttk.Frame(context.root, borderwidth=1, relief=SOLID, padding=[10, 10])
        inputFrame.grid(row=0, column=0, sticky="nsew")

        input_name = ttk.Label(inputFrame, text="Input Text")
        input_name.place(relx=0.5, anchor=CENTER)
        self.entry = Text(inputFrame, background="#E0FFFF")
        self.entry.place(relwidth=1, relheight=0.9, rely=0.1)
        self.entry.bind('<Return>', self.send_data)

    def send_data(self, event=None):
        data = self.entry.get("end-1c linestart", "end-1c lineend")
        self.context.write_data(data)
