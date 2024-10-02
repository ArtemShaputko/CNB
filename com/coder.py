from random import randint

def corrupt(data: bytes) -> bytes:
    data_polynom = int.from_bytes(data, byteorder='big')
    if randint(0,100) < 70:
        rand_bit = randint(0,data_polynom.bit_length() - 1)
        mask = 1 << rand_bit
        data_polynom = data_polynom ^ mask
    return data_polynom.to_bytes(len(data), byteorder='big')

def divide_polynoms(dividend: int, divider: int):
    quotient, current = 0, divider
    while True:
        if divider.bit_length() > dividend.bit_length():
            break
        coefficient = 1 << (dividend.bit_length() - divider.bit_length())
        current = divider << (dividend.bit_length() - divider.bit_length())
        quotient += coefficient
        dividend ^= current
    return quotient, dividend

def shift(num: int, length: int, count: int):
    mask = ((1 << length) - 1)
    if count > 0:
        count %= length
        count_bits = (1 << count) - 1
        last_bits = num & (count_bits << (length - count))
        return ((num << count) + (last_bits >> (length - count))) & mask
    elif count < 0:
        count = -count % length
        count_bits = (1 << count) - 1
        first_bits = num & count_bits
        return (num >> count) + (first_bits << (length-count))
    else:
        return num



class Coder:
    def __init__(self, polynom = 0b100011101, bits_num=28*8):
        self.data_bits = bits_num
        self.polynom = polynom
        self.control_bits = polynom.bit_length() - 1
        self.total_bits = self.data_bits + self.control_bits
        self.error_number = 1
        self.syndrome_table = {divide_polynoms(1 << a, polynom)[1] : a for a in range(self.total_bits)}


    def encode_data(self, data: bytes):
        data_polynom = int.from_bytes(data, byteorder='big')
        res = data_polynom << self.control_bits
        remainder = divide_polynoms(res, self.polynom)[1]
        res += remainder
        return res.to_bytes(int(self.total_bits / 8 ), byteorder='big')

    def decode_data(self, data: bytes) -> [bytes, int]:
        data_polynom = int.from_bytes(data, byteorder='big')
        remainder = divide_polynoms(data_polynom, self.polynom)[1]
        if remainder == 0:
            res = data_polynom >> self.control_bits
            return res.to_bytes(int(self.data_bits / 8), byteorder='big'), None
        else:
            res, error_pos = self.fix_error_table(data_polynom, remainder)
            res >>= self.control_bits
            return res.to_bytes(int(self.data_bits / 8), byteorder='big'), error_pos

    def fix_error_shift(self, data_polynom: int, remainder: int):
        weight = bin(remainder).count('1')
        count = 0
        while weight > self.error_number:
            count += 1
            data_polynom = shift(data_polynom, self.total_bits, 1)
            remainder = divide_polynoms(data_polynom, self.polynom)[1]
            weight = bin(remainder).count('1')
        data_polynom ^= remainder
        data_polynom = shift(data_polynom, self.total_bits, -count)
        return data_polynom

    def fix_error_table(self, data_polynom: int, remainder: int):
        try:
            error_pos = self.syndrome_table[remainder]
            return data_polynom ^ (1 << error_pos), error_pos
        except Exception as e:
            print(f"Ошибка поиска: {str(e)}")
            return data_polynom, None