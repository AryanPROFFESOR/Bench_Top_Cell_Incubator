"""Small PID controller with output clamping and anti-windup (conditional integration)."""


class PID:
    def __init__(self, kp, ki, kd, out_min=0.0, out_max=1.0):
        self.kp, self.ki, self.kd = kp, ki, kd
        self.out_min, self.out_max = out_min, out_max
        self._i = 0.0
        self._prev = None

    def reset(self):
        self._i, self._prev = 0.0, None

    def update(self, setpoint, measurement, dt):
        err = setpoint - measurement
        d = 0.0 if self._prev is None else (err - self._prev) / dt
        self._prev = err
        out = self.kp * err + self._i + self.kd * d
        if self.out_min < out < self.out_max:           # integrate only when not saturated
            self._i += self.ki * err * dt
        return max(self.out_min, min(self.out_max, out))
