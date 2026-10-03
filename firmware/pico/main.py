"""Incubator controller main loop (MicroPython on Raspberry Pi Pico W).

Every SAMPLE_PERIOD_S it reads the PT1000 (MAX31865) and SHT4x, optionally runs a PID
on a heater output, and prints one JSON line over USB serial. It also accepts text commands:
    EJECT | RETRACT | SET_TEMP <C> | STATUS
"""
import sys
import time
import json
import select

import config
import max31865
import sht4x
from servo import Servo
from pid import PID

try:
    from machine import Pin, PWM
except ImportError:  # allows importing for static checks on a PC
    Pin = PWM = None


def main():
    rtd = max31865.make(config)
    rh_sensor = sht4x.make(config)
    tray = Servo(config.SERVO_PINS[config.TRAY_SERVO])
    tray.write_angle(config.TRAY_ANGLE_RETRACTED)
    tray_state = "retracted"

    heater = None
    if config.PIN_HEATER is not None:
        heater = PWM(Pin(config.PIN_HEATER))
        heater.freq(config.HEATER_PWM_HZ)
        heater.duty_u16(0)
    pid = PID(kp=0.15, ki=0.01, kd=0.0)  # placeholder gains - tune on the real chamber
    setpoint = config.TARGET_TEMP_C

    poll = select.poll()
    poll.register(sys.stdin, select.POLLIN)
    last = time.ticks_ms()

    while True:
        # ---- commands from the PC ----
        if poll.poll(0):
            parts = sys.stdin.readline().strip().split()
            cmd = parts[0].upper() if parts else ""
            if cmd == "EJECT" and tray_state != "ejected":
                tray.sweep(config.TRAY_ANGLE_EJECTED, config.TRAY_MOVE_TIME_S)
                tray_state = "ejected"
            elif cmd == "RETRACT" and tray_state != "retracted":
                tray.sweep(config.TRAY_ANGLE_RETRACTED, config.TRAY_MOVE_TIME_S)
                tray_state = "retracted"
            elif cmd == "SET_TEMP" and len(parts) == 2:
                setpoint = max(20.0, min(40.0, float(parts[1])))
                pid.reset()

        # ---- periodic sample ----
        now = time.ticks_ms()
        if time.ticks_diff(now, last) >= config.SAMPLE_PERIOD_S * 1000:
            dt = time.ticks_diff(now, last) / 1000.0
            last = now
            msg = {"t": time.time(), "tray": tray_state, "setpoint_c": setpoint}
            try:
                temp = rtd.temperature_c()
                msg["temp_c"] = round(temp, 3)
                duty = pid.update(setpoint, temp, dt) if tray_state == "retracted" else 0.0
                if heater:
                    heater.duty_u16(int(duty * 65535))
                msg["heater"] = round(duty, 3)
            except OSError as e:
                msg["rtd_error"] = str(e)
                if heater:
                    heater.duty_u16(0)        # fail safe: heater off on sensor fault
            try:
                _, rh = rh_sensor.read()
                msg["rh_pct"] = round(rh, 1)
            except OSError as e:
                msg["rh_error"] = str(e)
            print(json.dumps(msg))
        time.sleep_ms(20)


main()
