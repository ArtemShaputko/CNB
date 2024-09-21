from tkinter import *
from tkinter import ttk


class OutputWindow:
    def __init__(self, context):
        self.outputFrame = ttk.Frame(context.root, borderwidth=1, relief=SOLID, padding=[10, 10])
        self.outputFrame.grid(row=0, column=1, sticky="nsew")

        output_name = ttk.Label(self.outputFrame, text="Received Text")
        output_name.place(relx=0.5, anchor=CENTER)
        self.text_read = Text(self.outputFrame, state=DISABLED, bg="#FFFACD")
        self.text_read.place(relwidth=1, relheight=0.9, rely=0.1)
        self.context = context

    def display_data(self, data):
        self.text_read.config(state=NORMAL)
        self.text_read.insert(END, data + '\n')
        self.text_read.config(state=DISABLED)
        self.text_read.yview(END)