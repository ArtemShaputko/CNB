from tkinter import *
from tkinter import ttk


class StationWindow:
    def __init__(self, context):
        self.context = context
        self.station_frame = ttk.Frame(context.root, borderwidth=1, relief=SOLID)

        self.station_frame.columnconfigure(0, weight=1)
        self.station_frame.columnconfigure(1, weight=1)
        self.station_frame.rowconfigure(0, weight=1)
        self.station_frame.rowconfigure(1, weight=1)
        self.station_frame.rowconfigure(2, weight=1)

        self.station_frame.grid(column=0, row=2, columnspan=2, sticky="nsew")

        station_name = ttk.Label(self.station_frame, text=f"Station {context.station.number}", anchor=N)
        station_name.grid(column=0, row=0, columnspan=2, sticky="nsew")

        select_station_label = ttk.Label(self.station_frame, text="Select message receiver:", anchor=N)
        select_station_label.grid(column=0, row=1, sticky="nsew")

        list_var = ['1', '2', '3']
        list_var.remove(f'{context.station.number}')
        self.station_var = StringVar()
        self.combo = ttk.Combobox(self.station_frame, textvariable=self.station_var, values=list_var)
        self.combo.grid(column=1, row=1)
        self.combo.set(list_var[0])

        select_priority_label = ttk.Label(self.station_frame, text="Select message priority:", anchor=N)
        select_priority_label.grid(column=0, row=2, sticky="nsew")

        self.priority_var = IntVar()
        self.priority = ttk.Combobox(self.station_frame, textvariable=self.priority_var, values=['0','1'])
        self.priority.grid(column=1, row=2)
        self.priority.set(0)