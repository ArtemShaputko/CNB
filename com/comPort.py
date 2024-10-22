import time

import serial

from com.coder import Coder, corrupt
import ring
from ring import write_debug_info

def is_stuff(data):
    return data == '$7A|' or data == '$7A7'


class ComPort:
    def __init__(self, context, station, ser = serial.Serial()):
        self.flag = '$|'
        self.context = context
        self.ser = ser
        self.bytes_sent = 0
        self.bytes_received = 0
        self.baudrate = ser.baudrate
        self.station = station

    def ring_communicate(self):
        try:
            while True:
                if self.ser.in_waiting > 0:
                    received_data = self.ser.read(self.ser.in_waiting)
                    self.bytes_received += len(received_data)
                    i = 0
                    while i < len(received_data):
                        packet_start = i
                        i+=2
                        while i < len(received_data) and received_data[i:i+2] != self.flag.encode():
                            i+=1
                        packet_len = i-packet_start
                        if packet_len < 5:
                            continue
                        packet = bytearray(received_data[packet_start:packet_start+packet_len])
                        if packet_len == 5 and self.token_check(packet):
                            write_debug_info(f'{self.station.number} received token')
                            if self.station.data_buffer:
                                self.write_with_priority(packet, self.station.data_buffer.pop(0))
                            self.station.write_data(bytes(packet))
                        elif self.station.is_monitor and packet[2] & 0b00001000 != 0:
                            write_debug_info(f'{self.station.number} detected cycle')
                        elif packet[5] == self.station.number:
                            write_debug_info(
                                f'{self.station.number} received own packet, deleting it')
                        else:
                            if self.station.is_monitor:
                                packet[2] |= 0b00001000
                            if packet[4] != self.station.number:
                                self.station.write_data(bytes(packet))
                                write_debug_info(f'{self.station.number} received data, destination is not station, resending it')
                            else:
                                write_debug_info(f'{self.station.number} received data')
                                buffer = packet.copy()
                                packet[36] = 0b11001100
                                self.station.write_data(bytes(packet))
                                write_debug_info(f'{self.station.number} data copied, resending it')
                                changes, error_pos = self.read_data(buffer[6:35])
                                self.context.statusWindow.show_packets(buffer, changes, error_pos)
                time.sleep(0.6)
        except Exception as e:
            print(f'Ошибка коммуникации {str(e)}')

    def token_check(self, token: bytearray):
        if token[2] & 0b00010000 == 0b00010000:
            if self.station.is_monitor:
                self.station.received_token = True
                token[2] |= 0b00001000
            token[2] &= 0b11110111
            return True
        return False

    def write_with_priority(self, token: bytearray, frame: [bytes, int]):
        ac = token[2]
        ac_tm = (ac & 0b00011000) >> 3
        priority_received = (ac & 0b11100000) >> 5 # priority in received token
        priority_transmit = priority_received      # priority, that will be in transmitted message
        reserved_received = ac & 0b00000111
        reserved_transmit = 0
        priority_frame = frame[1]                  # frame`s priority
        if priority_frame >= priority_received:
            self.station.packet_write_data(frame[0])
        else:
            if max(priority_frame, reserved_received) > priority_received:
                priority_transmit = max(priority_frame, reserved_received)
                self.station.stack_transmit.append(priority_transmit)
                self.station.stack_received.append(priority_received)
            else:
                if (not self.station.stack_received) or (priority_received != self.station.stack_transmit[-1]):
                    reserved_transmit = max(priority_frame, reserved_received)
                else:
                    if max(priority_frame, reserved_received) > self.station.stack_received[-1]:
                        priority_transmit = max(priority_frame, reserved_received)
                        self.station.stack_transmit.pop()
                        self.station.stack_transmit.append(priority_transmit)
                    else:
                        priority_transmit = self.station.stack_received[-1]
                        reserved_transmit = max(priority_frame, reserved_received)
                        self.station.stack_transmit.pop()
                        self.station.stack_received.pop()

        token[1] = (priority_transmit<<5) + (ac_tm << 3) + reserved_transmit


    def write_data(self, data):
        if data:
            try:
                bytes_to_send = len(data)
                self.ser.write(data)
                self.bytes_sent += bytes_to_send
                self.context.statusWindow.update_port_info(self.bytes_sent)
            except Exception as e:
                print(f"Ошибка записи: {str(e)}")

    def read_data(self, packet: bytes) -> [list[int], int]:
        coder = Coder()
        decoded_data, error_pos = coder.decode_data(packet)
        debyte_staff, changes = self.debyte_staff(decoded_data)
        self.context.outputWindow.display_data(debyte_staff)
        return changes, error_pos

    def packet_write(self, data: str):
        if data:
            data = self.byte_staff(data)
            i = 0
            while i < len(data):
                packet = bytearray()
                packet += bytearray(self.flag.encode())
                packet += 0b00010000.to_bytes(1, byteorder='big')
                packet += b'\0'
                packet += int(self.context.stationWindow.combo.get()).to_bytes(1, byteorder = 'big')                                                       # destination port
                packet += self.station.number.to_bytes(1, byteorder = 'big')
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
                packet += b'\0'
                packet += b'\0'
                ring.write_debug_info(f'Station {self.station.number} sending message to Station {self.context.stationWindow.combo.get()}')
                self.write_data(packet)
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

    def __del__(self):
        self.ser.close()