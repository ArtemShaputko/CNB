import threading
from tkinter import Tk

import serial

from com.comPort import ComPort
from window.controlWindow import ControlWindow
from window.inputWindow import InputWindow
from window.outputWindow import OutputWindow
from window.statusWindow import StatusWindow


class MainApp:
    def __init__(self, _root):
        self.root = _root
        self.root.title("COM Port Communication")

        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        input_port_name = "COM1"
        output_port_name = "COM2"

        self.inputComPort = ComPort(self, ser=serial.Serial(input_port_name,baudrate=9600))
        self.outputComPort = ComPort(self, ser=serial.Serial(output_port_name,baudrate=9600))

        self.controlWindow = ControlWindow(self, self.inputComPort.ser, self.outputComPort.ser)
        self.inputWindow = InputWindow(self)
        self.outputWindow = OutputWindow(self)
        self.statusWindow = StatusWindow(self, self.inputComPort)

        threading.Thread(target=self.read_data, daemon=True).start()

    def write_data(self, data):
        if data:
            try:
                self.inputComPort.packet_write(data)
            except Exception as e:
                print(f"Ошибка отправки: {str(e)}")

    def read_data(self):
        try:
            self.outputComPort.read_data()
        except Exception as e:
            print(f"Ошибка чтения: {str(e)}")

if __name__ == "__main__":
    root = Tk()
    root.geometry("700x400")
    app = MainApp(root)
    root.mainloop()