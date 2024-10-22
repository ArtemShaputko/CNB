import threading
from tkinter import Tk

from com.station import Station
from window.controlWindow import ControlWindow
from window.inputWindow import InputWindow
from window.debugWindow import DebugWindow
from window.outputWindow import OutputWindow
from window.stationWindow import StationWindow
from window.statusWindow import StatusWindow


def run_app(station_number: int, is_monitor: bool):
    MainApp(station_number, is_monitor)

class MainApp:
    def __init__(self, station_number: int, is_monitor: bool):
        self.root = Tk()
        self.root.geometry("800x500")
        self.root.title(f"COM Port Communication. Station №{station_number}")

        self.root.columnconfigure(0, weight=2)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=7)
        self.root.rowconfigure(1, weight=7)
        self.root.rowconfigure(2, weight=1)

        if station_number == 1:
            input_port_name = 'COM1'
            output_port_name = 'COM6'
        elif station_number == 2:
            input_port_name = 'COM3'
            output_port_name = 'COM2'
        else:
            input_port_name = 'COM5'
            output_port_name = 'COM4'

        self.station = Station(self, station_number, input_port_name, output_port_name, is_monitor)

        self.controlWindow = ControlWindow(self, self.station.inputComPort.ser, self.station.outputComPort.ser)
        self.inputWindow = InputWindow(self)
        self.outputWindow = OutputWindow(self)
        self.statusWindow = StatusWindow(self, self.station.inputComPort)
        self.stationWindow = StationWindow(self)

        if is_monitor:
            self.station.write_token()

        self.root.mainloop()


if __name__ == "__main__":
    threading.Thread(target=run_app, args=(1, True), daemon=True).start()
    threading.Thread(target=run_app, args=(2, False), daemon=True).start()
    threading.Thread(target=run_app, args=(3, False), daemon=True).start()
    DebugWindow()