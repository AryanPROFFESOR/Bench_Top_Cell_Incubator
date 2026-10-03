# Validation plan

Nothing below has been run yet. These are the acceptance tests planned for the build; results will go in `docs/results/`.

## 1. Electronics bring-up (bench)
1. Visual inspection, continuity and short checks (12 V, 5 V, 3.3 V, GND).
2. Power-up with a current-limited supply. Check 5 V is near 5.0 V and 3.3 V is near 3.3 V, under no load and with one servo moving.
3. Scope the buck output ripple under servo load.
4. Flash `firmware/pico`, confirm the SHT4x reads at address 0x44.
5. Replace the PT1000 with fixed precision resistors (for example 1000 ohm = 0 C, 1385 ohm = 100 C) and confirm the MAX31865 readings.

## 2. Temperature
- Sensor accuracy: compare the PT1000 chain against a calibrated reference thermometer at about 25, 37 and 40 C.
- Chamber: time to reach 37 C, overshoot, and steady-state stability over 24 h with the tray retracted.
- Tray cycle: temperature recovery time after an eject/retract cycle.

## 3. Humidity
- Hold RH near 95 % for 24 h; log RH and check for condensation on the optical window.

## 4. CO2 and N2 (when the gas route is decided)
- Verify the setpoint against a reference NDIR sensor, then log drift over several days.

## 5. Tray mechanics
- Positional repeatability over at least 100 eject/retract cycles (dial gauge or camera).
- Speed and smoothness; check there is no jamming or plate slip.
- Log gear wear on the printed rack and pinion.

## 6. Biological test (with the biologists)
- Culture stem cells in the chamber for several days, compared with a standard incubator control.
- Endpoints (for example viability and morphology) to be agreed with the lab.
