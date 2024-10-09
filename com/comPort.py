import time
from random import randint

import serial

from com.coder import Coder, corrupt

jam_signal = b'##'

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
            coder = Coder()
            while True:
                time.sleep(0.02)
                if self.ser.in_waiting > 0:
                    i = 0
                    received_data = self.ser.read(self.ser.in_waiting)
                    self.bytes_received += len(received_data)
                    while i < len(received_data):
                        if received_data[i+39:i+41] == jam_signal:
                            self.context.statusWindow.show_message("Received jam-signal")
                            i+=41
                            continue
                        decoded_data, error_pos = coder.decode_data(received_data[i+10:i+39])
                        debyte_staff, changes = self.debyte_staff(decoded_data[:-1])
                        self.context.statusWindow.show_packets(received_data[i : i+39],changes, error_pos)
                        self.context.outputWindow.display_data(debyte_staff)
                        i+=39
        except Exception as e:
            print(f"Ошибка чтения: {str(e)}")

    def packet_write(self, data: str):
        if data:
            data = self.byte_staff(data)
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
                data_field = data[i:i+data_len].ljust(28, '\x00')                # data
                coder = Coder()
                data_field = coder.encode_data(data_field.encode())
                data_field = corrupt(data_field)
                packet += data_field
                self.check_channel_busy()
                self.write_data_with_collisions(packet)
                i+=data_len

    def byte_staff(self, data):
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

    def debyte_staff(self, data: bytes):
        if data:
            changes = []
            res = bytearray()
            i = 0
            while i < len(data):
                if data[i:i + 4] == b'$7A|':
                    changes.append(i)
                    res += self.flag.encode()
                    i += 4
                elif data[i:i + 4] == b'$7A7':
                    changes.append(i)
                    res += b'$7'
                    i += 4
                else:
                    res.append(data[i])
                    i += 1
            return bytes(res), changes

    def write_data_with_collisions(self, data):
        global jam_signal
        counter = 0
        num_tries = 10
        while True:
            is_collision = randint(1,100) < 60
            self.write_data(data)
            if is_collision:
                self.context.statusWindow.show_message("Found collision, sending jam-signal")
                self.write_data(jam_signal)
                counter+=1
                if counter > num_tries:
                    self.context.statusWindow.show_message("Counter is bigger than threshold value, stopping sending")
                    break
                slots_num = randint(1, 1 << min(counter - 1, 10))
                time.sleep(slots_num*0.1)
            else:
                break

    def check_channel_busy(self):
        channel_is_busy = randint(1,100) > 50
        while not channel_is_busy:
            self.context.statusWindow.show_message("Channel is busy")
            channel_is_busy = randint(1, 100) > 50

    def __del__(self):
        self.ser.close()