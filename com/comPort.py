import serial

def is_stuff(data):
    return data == '$7A|' or data == '$7A7'

class ComPort:
    def __init__(self, context, ser = serial.Serial()):
        self.flag = '$|'
        self.context = context
        self.ser = ser
        self.bytes_sent = 0
        self.bytes_received = 0
        self.baudrate = ser.baudrate

    def write_data(self, data):
        if data:
            try:
                bytes_to_send = len(data)
                self.ser.write(data)
                self.bytes_sent += bytes_to_send
                self.context.statusWindow.update_port_info(self.bytes_sent)
            except Exception as e:
                print(f"Ошибка записи: {str(e)}")

    def read_data(self):
        try:
            while True:
                if self.ser.in_waiting > 0:
                    i = 0
                    received_data = self.ser.read(self.ser.in_waiting)
                    self.bytes_received += len(received_data)
                    while i < len(received_data):
                        decoded_data, changes = self.decode_data(received_data[i + 10: i + 39])
                        self.context.statusWindow.show_packets(received_data[i : i+39], changes)
                        self.context.outputWindow.display_data(decoded_data)
                        i+=39
        except Exception as e:
            print(f"Ошибка чтения: {str(e)}")

    def packet_write(self, data: str):
        if data:
            data = self.encode_data(data)
            i = 0
            while i < len(data):
                packet = bytearray()
                packet += bytearray(self.flag.encode())                                 # flag
                packet += b'\x00' * 4                                                   # destination port
                packet += self.ser.name[0:4].encode()                                   # source name
                data_len = 28
                for j in range(25, 28):
                    if is_stuff(data[i + j:i + j + 4]):
                        data_len = j
                        break
                data_field = data[i:i+data_len].ljust(28, '\x00')                       # data
                packet += data_field.encode()
                packet += b'\x00'                                                       # FCS
                self.write_data(packet)
                i+=data_len

    def encode_data(self, data):
        res = ''
        if data:
            i = 0
            while i < len(data):
                if data[i:i + 2] == self.flag:
                    res += '$7A|'
                    i += 2
                elif data[i:i + 2] == '$7':
                    res += '$7A7'
                    i += 2
                else:
                    res += data[i]
                    i += 1
        return res

    def decode_data(self, data):
        if data:
            data = data.decode()
            changes = []
            res = ''
            i = 0
            while i < len(data):
                if data[i:i + 4] == '$7A|':
                    changes.append(i)
                    res += self.flag
                    i += 4
                elif data[i:i + 4] == '$7A7':
                    changes.append(i)
                    res += '$7'
                    i += 4
                else:
                    res += data[i]
                    i += 1
            return res, changes

    def __del__(self):
        self.ser.close()