"""Desktop unit tests for the hardware-independent maths (run: python -m unittest discover firmware/tests)."""
import os
import sys
import types
import unittest

# stub the MicroPython 'machine' module so the drivers can be imported on a PC
sys.modules.setdefault("machine", types.SimpleNamespace(Pin=object, SPI=object, I2C=object, PWM=object))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "pico"))

import max31865  # noqa: E402
import sht4x     # noqa: E402
from pid import PID  # noqa: E402


class TestPT1000(unittest.TestCase):
    def test_zero_celsius(self):
        self.assertAlmostEqual(max31865.resistance_to_temp_c(1000.0), 0.0, places=6)

    def test_100_celsius(self):  # IEC 60751: PT1000 = 1385.055 ohm at 100 C
        self.assertAlmostEqual(max31865.resistance_to_temp_c(1385.055), 100.0, places=1)

    def test_37_celsius(self):
        r = 1000.0 * (1 + 3.9083e-3 * 37 + -5.775e-7 * 37 ** 2)
        self.assertAlmostEqual(max31865.resistance_to_temp_c(r), 37.0, places=6)


class TestSHT4x(unittest.TestCase):
    def test_crc_datasheet_vector(self):  # Sensirion application note: CRC(0xBEEF) = 0x92
        self.assertEqual(sht4x.crc8(bytes([0xBE, 0xEF])), 0x92)

    def test_conversion_limits(self):
        t, rh = sht4x.convert(0, 0)
        self.assertAlmostEqual(t, -45.0)
        self.assertEqual(rh, 0.0)               # clamped (-6 % raw)
        t, rh = sht4x.convert(65535, 65535)
        self.assertAlmostEqual(t, 130.0)
        self.assertEqual(rh, 100.0)             # clamped (119 % raw)


class TestPID(unittest.TestCase):
    def test_output_clamped(self):
        pid = PID(1.0, 0.0, 0.0, 0.0, 1.0)
        self.assertEqual(pid.update(37.0, 20.0, 1.0), 1.0)
        self.assertEqual(pid.update(37.0, 40.0, 1.0), 0.0)


if __name__ == "__main__":
    unittest.main()
