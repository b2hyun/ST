# Fine-Screw Loading Tool · Controlled Release — CAD

Parametric CadQuery model of the sample-loading tool and one jaw pair of the
target fixture.

The fixture is a C-frame with a fixed centre bar. On each side an orange jaw
is pushed **outward** by springs, clamping a 7×7 mm sample between the jaw
nose and the outer blue jaw. The purple loading tool sits on top of a jaw
pair: its downward pins drop into engagement sockets on the orange jaws
(the yellow-highlighted spots in the hand sketch), and a fine-pitch screw
with opposed LH/RH threads pulls **both jaws inward from both sides**,
compressing the springs and opening both sample gaps. Reversing the screw
slowly releases the springs so the samples are clamped gently.

The model is positioned in the **engaged state**: jaws pulled inward,
springs compressed, both sample gaps open with samples inserted.

## Files

| File | Description |
|---|---|
| `fine_screw_loading_tool.py` | Parametric model (CadQuery ≥ 2.8). Run to regenerate. |
| `fine_screw_loading_tool.step` | STEP AP214 assembly, 16 named + colored solids (tool + fixture reference). |
| `preview_tool.png` | Rendered preview (iso + side view). |

## Design choices / improvements over the sketch

1. **Two pins per carrier (4 total)** — matches the four yellow engagement
   points; the pin pair also reacts the screw torque so the tool cannot spin.
2. **Square guide spine between the carriers** — keeps the pins aligned while
   the tool is handled off the fixture and carries torque reaction.
3. **Chamfered pin tips + 0.1 mm radial socket clearance** — easy drop-in.
4. **Opposed-thread screw (turnbuckle action)** — one knob pulls both
   carriers symmetrically; recommended M5×0.5, RH one half / LH the other
   (threads are cosmetic and not modeled in the STEP).
5. **12-flat knob** for controlled slow release.

## Notes

- All dimensions in mm. Envelope of the modeled pair ≈ 120 × 70 × 41 mm.
- Jaw/bar dimensions are parametric guesses scaled from the 7×7 mm sample —
  measure the real fixture and update the parameters at the top of the
  script, then rerun to regenerate the STEP.
- The fixture parts (floor, centre bar, jaws, springs, samples) are included
  as reference geometry for fit checking; the tool itself is the four
  `tool_*` solids.
- Interference-checked: all part pairs report zero overlap volume.

## Regenerate

```bash
pip install cadquery
python cad/fine_screw_loading_tool.py
```
