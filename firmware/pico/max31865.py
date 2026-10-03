"""Minimal MicroPython driver for the MAX31865 RTD-to-digital converter (PT1000, 4-wire)."""
import time
from math import sqrt
from machine import Pin, SPI

_REG_CONFIG = 0x00
_REG_RTD_MSB = 0x01
_REG_FAULT = 0x07

_CFG_BIAS = 0x80
_CFG_ONESHOT = 0x20
_CFG_3WIRE = 0x10
_CFG_FAULT_CLEAR = 0x02
_CFG_FILTER_50HZ = 0x01

# Callendar-Van Dusen coefficients (IEC 60751), valid for T >= 0 C
_A = 3.9083e-3
_B = -5.775e-7


def resistance_to_temp_c(r_rtd, r0=1000.0):
    """Invert R = R0 (1 + A T + B T^2) for T >= 0 C."""
    return (-_A + sqrt(_A * _A - 4.0 * _B * (1.0 - r_rtd / r0))) / (2.0 * _B)


class MAX31865:
    def __init__(self, spi, cs, r_ref=4300.0, r_nominal=1000.0, wires=4, filter_50hz=True):
        self.spi, self.cs = spi, cs
        self.r_ref, self.r_nominal = r_ref, r_nominal
        self._cfg = (_CFG_3WIRE if wires == 3 else 0) | (_CFG_FILTER_50HZ if filter_50hz else 0)
        self.cs.value(1)
        self._write(_REG_CONFIG, self._cfg | _CFG_FAULT_CLEAR)

    def _write(self, reg, value):
        self.cs.value(0)
        self.spi.write(bytes([reg | 0x80, value]))
        self.cs.value(1)

    def _read(self, reg, n=1):
        self.cs.value(0)
        self.spi.write(bytes([reg & 0x7F]))
        data = self.spi.read(n)
        self.cs.value(1)
        return data

    def fault(self):
        return self._read(_REG_FAULT)[0]

    def read_raw(self):
        """One-shot conversion; returns the 15-bit ADC code."""
        self._write(_REG_CONFIG, self._cfg | _CFG_BIAS | _CFG_FAULT_CLEAR)
        time.sleep_ms(10)                      # bias settling
        self._write(_REG_CONFIG, self._cfg | _CFG_BIAS | _CFG_ONESHOT | _CFG_FAULT_CLEAR)
        time.sleep_ms(70)                      # conversion time (50 Hz filter)
        msb, lsb = self._read(_REG_RTD_MSB, 2)
        self._write(_REG_CONFIG, self._cfg)    # bias off to limit self-heating
        if lsb & 0x01:
            raise OSError("MAX31865 fault flag, status=0x%02X" % self.fault())
        return ((msb << 8) | lsb) >> 1

    def resistance(self):
        return self.read_raw() / 32768.0 * self.r_ref

    def temperature_c(self):
        return resistance_to_temp_c(self.resistance(), self.r_nominal)


def make(config):
    spi = SPI(config.SPI_ID, baudrate=500_000, polarity=0, phase=1,
              sck=Pin(config.PIN_SPI_SCK), mosi=Pin(config.PIN_SPI_MOSI), miso=Pin(config.PIN_SPI_MISO))
    cs = Pin(config.PIN_SPI_CS, Pin.OUT, value=1)
    return MAX31865(spi, cs, config.RTD_REF_OHM, config.RTD_NOMINAL_OHM, config.RTD_WIRES,
                    config.MAINS_FILTER_HZ == 50)
