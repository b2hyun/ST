# Fine-Screw Loading Tool · Controlled Release — CAD

Parametric CadQuery model of the sample-loading tool and one jaw pair of the
target fixture.

The fixture is a C-frame with a fixed centre bar. On each side an orange jaw
is pushed **outward** by springs, clamping a 7×7 mm sample between the jaw
nose and the outer blue jaw. The purple loading tool is dropped in from above
through the fixture's thickness: each carrier has two **L-shaped hook shoes
form-fitted to the outer corners of an orange jaw** (the four
yellow-highlighted engagement spots in the hand sketch), so it fits snugly
into place. A fine-pitch screw with opposed LH/RH threads then pulls **both
jaws inward from both sides**, compressing the springs and opening both
sample gaps. Reversing the screw slowly releases the springs so the samples
are clamped gently, after which the tool lifts straight out.

The model is positioned in the **engaged state**: jaws pulled inward,
springs compressed, both sample gaps open with samples inserted.

## Files

| File | Description |
|---|---|
| `fine_screw_loading_tool.py` | Parametric model (CadQuery ≥ 2.8). Run to regenerate. |
| `fine_screw_loading_tool.step` | STEP AP214 assembly, 16 named + colored solids (tool + fixture reference). |
| `preview_tool.png` | Rendered preview (iso + side view). |

## Design choices

1. **Form-fitted corner hooks (4 total)** — each L-shaped hook pocket wraps
   one jaw corner on two faces (outer shoulder + side) with 0.1 mm fit
   clearance, matching the four yellow engagement points; the shoulder faces
   beside the nose are the pulling surfaces and the pockets also react the
   screw torque.
2. **Hooks pass beside the sample gap** — they never touch the sample or the
   outer blue jaw.
3. **Square guide spine between the carriers** — keeps the hooks aligned
   while the tool is handled off the fixture.
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
