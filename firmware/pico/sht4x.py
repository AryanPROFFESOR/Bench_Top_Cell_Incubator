"""Minimal MicroPython driver for the Sensirion SHT4x (I2C, 0x44)."""
import time
from machine import Pin, I2C

_CMD_MEASURE_HIGH = b"\xFD"
_CMD_SOFT_RESET = b"\x94"


def crc8(data):
    crc = 0xFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = ((crc << 1) ^ 0x31) & 0xFF if crc & 0x80 else (crc << 1) & 0xFF
    return crc


def convert(raw_t, raw_rh):
    temp_c = -45.0 + 175.0 * raw_t / 65535.0
    rh = max(0.0, min(100.0, -6.0 + 125.0 * raw_rh / 65535.0))
    return temp_c, rh


class SHT4x:
    def __init__(self, i2c, addr=0x44):
        self.i2c, self.addr = i2c, addr
        self.i2c.writeto(self.addr, _CMD_SOFT_RESET)
        time.sleep_ms(2)

    def read(self):
        """Return (temperature_C, relative_humidity_percent), high-precision mode."""
        self.i2c.writeto(self.addr, _CMD_MEASURE_HIGH)
        time.sleep_ms(10)
        b = self.i2c.readfrom(self.addr, 6)
        if crc8(b[0:2]) != b[2] or crc8(b[3:5]) != b[5]:
            raise OSError("SHT4x CRC error")
        return convert((b[0] << 8) | b[1], (b[3] << 8) | b[4])


def make(config):
    i2c = I2C(config.I2C_ID, sda=Pin(config.PIN_I2C_SDA), scl=Pin(config.PIN_I2C_SCL), freq=100_000)
    return SHT4x(i2c, config.SHT4X_ADDR)
