# Design review notes (checklist for the next revision)

A self-review of the current schematic. Items are things to confirm or fix before ordering boards.

| # | Item | Why it matters |
|---|---|---|
| 1 | L1 is labelled `33uF` in the schematic; it should read 33 uH. | Wrong unit in the schematic value field. |
| 2 | L1 and D1 use 0603 footprints. | A 0603 inductor and diode cannot carry the buck's current at up to 3 A. Select a power inductor and a Schottky in a proper package (for example SMA/SMB) and update the footprints. Check values against the TPS5430 datasheet. |
| 3 | R9 and R10 (I2C pull-ups) have the value `R` in the schematic; the documentation says 10 kohm. | Set the value so the BOM is correct. |
| 4 | No 12 V input connector, fuse or reverse-polarity protection is in the schematic. | Add a terminal block, fuse and TVS or reverse protection. |
| 5 | No heater driver. | Temperature regulation needs an output stage (MOSFET or SSR) for the heater. |
| 6 | Five servos share one 5 V, 3 A rail with the logic supply. | Check the combined stall current; consider limiting how many servos run at once. |
| 7 | The layout figure is labelled "prior to ground plane pour". | Complete the pour and re-run DRC before fabrication. |
| 8 | SHT4x is a 1.5 x 1.5 mm DFN. | Very hard to hand-solder; consider a reflow stencil or a breakout. |
| 9 | `PCB_EMBL.kicad_pcb` was empty (79 bytes) in the exported project. | Save the layout in KiCad and add the file to `hardware/pcb/kicad/`. |
