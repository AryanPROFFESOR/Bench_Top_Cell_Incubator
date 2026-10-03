"""Pin map and constants for the stage-top incubator control PCB (Raspberry Pi Pico W).

Pins marked VERIFIED come from the PCB hardware documentation / schematic.
Anything marked TODO is not on the current board and must be decided with the lab.
"""

# --- SPI0 -> MAX31865 RTD-to-digital converter (U3) --- VERIFIED
SPI_ID = 0
PIN_SPI_MISO = 16
PIN_SPI_CS = 17
PIN_SPI_SCK = 18
PIN_SPI_MOSI = 19

# --- I2C0 -> SHT4x humidity / temperature sensor (U4), 10 k pull-ups on board --- VERIFIED
I2C_ID = 0
PIN_I2C_SDA = 8
PIN_I2C_SCL = 9
SHT4X_ADDR = 0x44

# --- PWM servo headers J1..J5 (5 V, GND, signal via 220 ohm) --- VERIFIED
SERVO_PINS = {"J1": 0, "J2": 1, "J3": 2, "J4": 3, "J5": 4}
TRAY_SERVO = "J1"           # which header drives the rack-and-pinion tray (assignment is a choice)

# --- MAX31865 / PT1000 --- VERIFIED
RTD_NOMINAL_OHM = 1000.0    # PT1000
RTD_REF_OHM = 4300.0        # R8, 4.3 k 0.1 %
RTD_WIRES = 4               # 4-wire (FORCE+/-, RTDIN+/-)
MAINS_FILTER_HZ = 50        # 50 Hz mains (Europe / India)

# --- Control targets (from the design proposal) ---
TARGET_TEMP_C = 37.0
TARGET_RH_PCT = 95.0
TARGET_CO2_PCT = 5.0        # CO2 control is external / not on this PCB yet

# --- Tray calibration: measure on the real assembly, then edit --- TODO
TRAY_ANGLE_RETRACTED = 0.0  # servo angle (deg) with tray fully inside
TRAY_ANGLE_EJECTED = 180.0  # servo angle (deg) with tray fully out
TRAY_MOVE_TIME_S = 2.0      # time to sweep between the two positions

# --- Heater output (NOT on the current PCB; needs an external MOSFET/SSR driver) --- TODO
PIN_HEATER = None           # set to a free GPIO number once a driver stage exists
HEATER_PWM_HZ = 2           # slow PWM / time-proportioning for an SSR

SAMPLE_PERIOD_S = 2.0
