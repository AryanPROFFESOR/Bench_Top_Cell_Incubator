"""PWM servo helper (50 Hz, 500-2500 us pulse)."""
import time
from machine import Pin, PWM

_PERIOD_US = 20000


class Servo:
    def __init__(self, pin, min_us=500, max_us=2500, max_deg=180.0):
        self.pwm = PWM(Pin(pin))
        self.pwm.freq(50)
        self.min_us, self.max_us, self.max_deg = min_us, max_us, max_deg
        self.angle = None

    def write_us(self, pulse_us):
        self.pwm.duty_u16(int(pulse_us * 65535 / _PERIOD_US))

    def write_angle(self, deg):
        deg = max(0.0, min(self.max_deg, deg))
        self.write_us(self.min_us + (self.max_us - self.min_us) * deg / self.max_deg)
        self.angle = deg

    def sweep(self, target_deg, duration_s, steps=50):
        """Move smoothly (linear ramp) so the tray does not jerk the sample plate."""
        start = self.angle if self.angle is not None else target_deg
        for i in range(1, steps + 1):
            self.write_angle(start + (target_deg - start) * i / steps)
            time.sleep(duration_s / steps)

    def release(self):
        self.pwm.duty_u16(0)
