# Roadmap and open questions

## Status

| Area | Status |
|---|---|
| Control PCB schematic | Complete, DRC clean (per hardware documentation) |
| PCB layout | Routed; final ground-plane pour and export pending |
| Temperature and humidity sensing | Designed (PT1000 + MAX31865, SHT4x) |
| Servo outputs | 5 channels, designed |
| Reference firmware | Written; sensor maths unit-tested on a PC; not yet run on hardware |
| PC dashboard | Written; not yet run against hardware |
| CAD (SolidWorks) | Shell, chamber, tray, rack and pinion, bracket modelled; final work pending |
| CO2 and N2 control | Not on the PCB. Assumed external for now |
| Heater drive | Not on the PCB. Needs an external driver stage |

## Questions to settle with the lab (these block the CAD finalisation)
1. **Microscope mounting.** Is the incubator hard-mounted on the stage, or does it rest on it?
2. **Gas routing.** Is there an existing CO2/N2 mixer to tap (push-to-connect fittings only), or should the device switch the gas itself with valves?
3. **Electronics placement.** Inside the side-car cavity, or in an external desktop box?

## Next steps
- Finalise CAD once the three answers are known; add flanges or dovetails for the stage.
- Choose a heater (for example a film heater with a MOSFET or SSR stage) and a CO2 sensor.
- Choose the actuator for the tray: the current board drives hobby servos. A stepper (for example NEMA 17 with a driver module) would give more precise open-loop positioning and unlimited rotation; this would need a driver and limit-switch inputs.
- Print, assemble and run the [validation plan](test_plan.md).
- Add automatic image transfer to a server, remote access and image analysis (see `software/pipeline/`).
