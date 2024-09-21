import serial

class ComPort:
    def __init__(self, context, ser = serial.Serial()):
        self.context = context
        self.ser = ser
        self.bytes_sent = 0
        self.bytes_received = 0
        self.baudrate = ser.baudrate

    def write_data(self, data):
        if data:
            try:
                bytes_to_send = len(data)
                self.ser.write(data.encode())
                self.bytes_sent += bytes_to_send
                self.context.statusWindow.update_port_info(self.bytes_sent)
            except Exception as e:
                print(f"Ошибка записи: {str(e)}")

    def read_data(self):
        try:
            while True:
                if self.ser.in_waiting > 0:
                    received_data = self.ser.read(self.ser.in_waiting).decode()
                    self.bytes_received += len(received_data)
                    self.context.outputWindow.display_data(received_data)
        except Exception as e:
            print(f"Ошибка чтения: {str(e)}")

    def __del__(self):
        self.ser.close()


