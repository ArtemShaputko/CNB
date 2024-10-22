import threading
import time

import serial

from com.comPort import ComPort


class Station:
    def __init__(self, context, number: int, input_port_name: str , output_port_name: str, is_monitor: bool):
        self.received_token = False
        self.context = context
        self.number = number
        self.input_port_name = input_port_name
        self.output_port_name = output_port_name

        self.data_buffer = list()
        self.stack_transmit = list()
        self.stack_received = list()
        self.is_monitor = is_monitor

        self.inputComPort = ComPort(context, self, ser=serial.Serial(input_port_name, baudrate=9600))
        self.outputComPort = ComPort(context, self, ser=serial.Serial(output_port_name, baudrate=9600))

        if is_monitor:
            threading.Thread(target=self.check_token, daemon=True).start()

        threading.Thread(target=self.read_data, daemon=True).start()

    def check_token(self):
        while True:
            time.sleep(2.6)
            if not self.received_token:
                self.write_token()
            else:
                self.received_token = False

    def write_token(self):
        self.write_data(self.outputComPort.flag.encode() + b'\x18\x00\x00')

    def write_data(self, data):
        if data:
            try:
                self.outputComPort.write_data(data)
            except Exception as e:
                print(f"Ошибка отправки: {str(e)}")

    def packet_write_data(self, data):
        if data:
            try:
                self.outputComPort.packet_write(data)
            except Exception as e:
                print(f"Ошибка отправки: {str(e)}")

    def read_data(self):
        try:
            self.inputComPort.ring_communicate()
        except Exception as e:
            print(f"Ошибка чтения: {str(e)}")