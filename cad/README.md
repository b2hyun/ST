# Four-Point Fitted Hook Tool · Controlled Release — CAD

Parametric CadQuery model of the concept fixture: a fine-pitch screw with
opposed (LH/RH) threads drives two nut blocks inward by equal amounts. Each
block carries a hook carrier whose two fitted shoes engage dedicated grooves
on the block faces (4 engagement points total). Two 7×7 mm samples are clamped
between the block inner faces and a central datum plate.

## Files

| File | Description |
|---|---|
| `four_point_hook_tool.py` | Parametric model (CadQuery ≥ 2.8). Run to regenerate outputs. |
| `four_point_hook_tool.step` | STEP AP214 assembly, 15 named + colored solids. |
| `preview.png` | Rendered preview. |

## Improvements over the original sketch

1. **Base plate with guide rib** — each block has a matching bottom groove, so
   screw torque cannot rotate the blocks and travel stays straight.
2. **Defined shoe engagement** — the four "fitted shoe" contacts are modeled as
   chamfered lips dropping into chamfered grooves on the block faces
   (0.2 mm sliding clearance) for a repeatable fit.
3. **Preload springs on both sides** — remove opposed-thread backlash so the
   slow reverse release stays smooth (no lash jump).
4. **Thrust washers** between blocks and springs.
5. **Screw clearance hole** through the central datum plate.
6. **12-flat knob** for controlled grip.

## Notes

- All dimensions in mm; overall envelope ≈ 168 × 60 × 58 mm.
- Threads are not modeled (cosmetic in STEP). Recommended: **M8×0.75**,
  RH on one screw half, LH on the other.
- Model is positioned at the *closed-on-sample* state: block inner faces at
  ±8.5 mm, i.e. datum plate (3 mm) + one 7 mm sample per side.
- Concept only — final hook profile, clearances, travel, thread pitch and
  spring force still require measurement, as noted on the source drawing.

## Regenerate

```bash
pip install cadquery
python cad/four_point_hook_tool.py
```
