"""PyQt5 dashboard for the stage-top incubator.

Reads the JSON lines printed by firmware/pico/main.py over USB serial, shows live temperature /
humidity / tray state, sends EJECT / RETRACT / SET_TEMP commands, and logs every sample to CSV.

    pip install -r software/requirements.txt
    python software/gui/incubator_gui.py --port COM5        # Windows
    python software/gui/incubator_gui.py --port /dev/ttyACM0  # Linux / macOS
"""
import argparse
import csv
import json
import sys
import time
from pathlib import Path

import serial
from PyQt5 import QtCore, QtWidgets

FIELDS = ["time_iso", "temp_c", "setpoint_c", "rh_pct", "heater", "tray"]


class SerialWorker(QtCore.QThread):
    sample = QtCore.pyqtSignal(dict)
    error = QtCore.pyqtSignal(str)

    def __init__(self, port, baud=115200):
        super().__init__()
        self.ser = serial.Serial(port, baud, timeout=0.2)
        self._run = True

    def send(self, line):
        self.ser.write((line + "\n").encode())

    def run(self):
        while self._run:
            try:
                raw = self.ser.readline().decode(errors="ignore").strip()
                if raw.startswith("{"):
                    self.sample.emit(json.loads(raw))
            except (serial.SerialException, json.JSONDecodeError) as exc:
                self.error.emit(str(exc))
                time.sleep(0.5)

    def stop(self):
        self._run = False
        self.wait(1000)
        self.ser.close()


class Window(QtWidgets.QWidget):
    def __init__(self, worker, log_path):
        super().__init__()
        self.worker = worker
        self.setWindowTitle("Bench-Top Cell Incubator")
        self.temp = QtWidgets.QLabel("-- °C")
        self.rh = QtWidgets.QLabel("-- % RH")
        self.tray = QtWidgets.QLabel("tray: --")
        self.status = QtWidgets.QLabel("waiting for data...")
        for lab in (self.temp, self.rh):
            lab.setStyleSheet("font-size: 32px; font-weight: 600;")
        self.setpoint = QtWidgets.QDoubleSpinBox()
        self.setpoint.setRange(20.0, 40.0)
        self.setpoint.setValue(37.0)
        self.setpoint.setSuffix(" °C")
        b_set = QtWidgets.QPushButton("Apply setpoint")
        b_out = QtWidgets.QPushButton("Eject tray")
        b_in = QtWidgets.QPushButton("Retract tray")
        b_set.clicked.connect(lambda: worker.send("SET_TEMP %.2f" % self.setpoint.value()))
        b_out.clicked.connect(lambda: worker.send("EJECT"))
        b_in.clicked.connect(lambda: worker.send("RETRACT"))

        grid = QtWidgets.QGridLayout(self)
        grid.addWidget(self.temp, 0, 0)
        grid.addWidget(self.rh, 0, 1)
        grid.addWidget(self.tray, 1, 0, 1, 2)
        grid.addWidget(self.setpoint, 2, 0)
        grid.addWidget(b_set, 2, 1)
        grid.addWidget(b_out, 3, 0)
        grid.addWidget(b_in, 3, 1)
        grid.addWidget(self.status, 4, 0, 1, 2)

        new = not log_path.exists()
        self.log = open(log_path, "a", newline="")
        self.writer = csv.DictWriter(self.log, fieldnames=FIELDS)
        if new:
            self.writer.writeheader()
        worker.sample.connect(self.on_sample)
        worker.error.connect(lambda m: self.status.setText("serial error: " + m))

    def on_sample(self, s):
        if "temp_c" in s:
            self.temp.setText("%.2f °C" % s["temp_c"])
        if "rh_pct" in s:
            self.rh.setText("%.1f %% RH" % s["rh_pct"])
        self.tray.setText("tray: %s" % s.get("tray", "--"))
        errs = [k for k in s if k.endswith("_error")]
        self.status.setText("sensor error: " + ", ".join(errs) if errs else "ok")
        row = {k: s.get(k, "") for k in FIELDS if k != "time_iso"}
        row["time_iso"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        self.writer.writerow(row)
        self.log.flush()

    def closeEvent(self, event):
        self.worker.stop()
        self.log.close()
        event.accept()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", required=True)
    ap.add_argument("--log", default="incubator_log.csv")
    args = ap.parse_args()
    app = QtWidgets.QApplication(sys.argv)
    worker = SerialWorker(args.port)
    win = Window(worker, Path(args.log))
    worker.start()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
