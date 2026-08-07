# Fine-Screw Loading Tool + spring-jaw fixture pair (concept CAD)
#
# Context: the fixture is a C-frame with a fixed centre bar. On each side an
# orange jaw is pushed OUTWARD by springs, clamping a 7x7 mm sample between the
# jaw nose and the outer blue jaw. The purple loading tool is dropped in from
# above through the fixture's thickness: each carrier has two L-shaped hook
# shoes whose pockets are form-fitted to the outer corners of an orange jaw
# (the four yellow-highlighted engagement spots). A fine-pitch screw with
# opposed (LH/RH) threads then pulls both carriers - and with them both jaws -
# inward from both sides, compressing the springs and opening both sample
# gaps. Reversing the screw slowly releases the springs so the samples are
# clamped gently, after which the tool lifts straight out.
#
# The model is positioned in the ENGAGED state: tool fitted, jaws pulled
# inward, springs compressed, both sample gaps open with samples inserted.
#
# Design details:
#   - hook shoes wrap each jaw corner on two faces (outer shoulder + side)
#     with 0.1 mm fit clearance, so the tool self-locates when dropped in
#     and the corner pockets react the screw torque
#   - the shoulder faces beside the jaw nose are the pulling surfaces; the
#     hooks pass beside the sample gap without touching sample or outer jaw
#   - square guide spine keeps the carriers aligned while handled
#   - 12-flat knob for controlled slow release
#
# Threads are not modeled (cosmetic in STEP); recommended: M5x0.5, RH on one
# screw half / LH on the other. All dimensions in mm, parametric guesses
# scaled from the 7x7 mm sample - real jaw dimensions require measurement.

import cadquery as cq

# ---- fixture parameters (X = clamp axis, Y = along centre bar, Z = up) ------
#
# MEASURED (from the 3 / 4 / 3 sketch): across the face the tool engages, the
# jaw is 3 + 4 + 3 = 10 mm - a 4 mm nose with a 3 mm shoulder either side.
# Those two 3 mm shoulders are the tool's push faces.
#
# ASSUMED, still to be measured: jaw length and height, nose length, centre
# bar and spring gap - scaled to suit the 10 mm width. Sample thickness is
# taken as a thin wafer coupon (7x7 mm face, ~1 mm thick), which is what sets
# the stroke; if the coupons are actually 7 mm thick, raise SAMPLE_T and the
# whole travel grows with it.
SAMPLE = 7.0              # coupon face, 7 x 7 mm
SAMPLE_T = 1.0            # ASSUMED coupon thickness, along the clamp axis
BAR_HALF = 2.0            # ASSUMED centre bar half-thickness
BAR_H = 10.0
SPRING_GAP = 3.0          # ASSUMED bar-to-jaw gap when compressed
JAW_X0 = BAR_HALF + SPRING_GAP          # orange jaw inner face
JAW_L, JAW_W, JAW_H = 7.0, 10.0, 8.0    # W = 3+4+3 MEASURED; L, H assumed
NOSE_L, NOSE_W = 3.5, 4.0               # NOSE_W = 4 MEASURED; length assumed
GAP_OPEN = SAMPLE_T + 1.0  # open sample gap = coupon + clearance
BLUE_X0 = JAW_X0 + JAW_L + NOSE_L + GAP_OPEN
SPRING_Y = 0.0                          # one light spring per side, on centre

# ---- tool parameters --------------------------------------------------------
FIT_CLR = 0.1                 # form-fit clearance of the hook pockets
HOOK_T = 1.5                  # hook blade thickness
HOOK_Z0 = 3.0                 # hooks reach down to this height
CAR_X0, CAR_X1 = 4.0, 13.0    # right carrier footprint
CAR_W, CAR_Z0, CAR_Z1 = 14.0, 8.5, 14.0
SCREW_D, SCREW_Z = 3.0, 11.5
SPINE, SPINE_Y = 3.0, 5.0     # square guide spine, offset from screw axis

# ---- fixture: floor + centre bar --------------------------------------------
floor = (
    cq.Workplane("XY", origin=(0, 0, -2))
    .box(56, 28, 2, centered=(True, True, False))
)
bar = cq.Workplane("XY").box(2 * BAR_HALF, 24, BAR_H, centered=(True, True, False))

# ---- fixture: orange spring jaw (right; left mirrored) ----------------------
jaw_r = (
    cq.Workplane("XY", origin=(JAW_X0 + JAW_L / 2, 0, 0))
    .box(JAW_L, JAW_W, JAW_H, centered=(True, True, False))
    .union(
        cq.Workplane("XY", origin=(JAW_X0 + JAW_L + NOSE_L / 2, 0, 0))
        .box(NOSE_L, NOSE_W, JAW_H, centered=(True, True, False))
    )
)
# the two outer corners beside the nose (the yellow spots) are the
# engagement shoulders the tool hooks fit onto - no extra features needed

# ---- fixture: blue outer jaw + sample ---------------------------------------
blue_jaw_r = (
    cq.Workplane("XY", origin=(BLUE_X0 + 2.5, 0, 0))
    .box(5, JAW_W, 7, centered=(True, True, False))
)
sample_r = (
    cq.Workplane("XY", origin=(BLUE_X0 - GAP_OPEN / 2, 0, 0))
    .box(SAMPLE_T, SAMPLE, SAMPLE, centered=(True, True, False))
)

# ---- fixture: compressed springs (2 per side) -------------------------------
def make_spring(x_start, length, radius=1.4, wire_r=0.3, turns=5, y=0.0, z=4.0):
    pitch = length / turns
    helix = cq.Wire.makeHelix(pitch, length, radius)
    spring = (
        cq.Workplane("XZ")
        .center(radius, 0)
        .circle(wire_r)
        .sweep(cq.Workplane("XY").newObject([helix]), isFrenet=True)
    )
    return spring.rotate((0, 0, 0), (0, 1, 0), 90).translate((x_start, y, z))

# inset by the wire radius so the coil ends don't cross the contact faces
_s0 = BAR_HALF + 0.3 + 0.05
_slen = SPRING_GAP - 2 * (0.3 + 0.05)
springs_r = make_spring(_s0, _slen, y=SPRING_Y)

# ---- tool: carriers with form-fitted corner hooks ---------------------------
# Each hook is an L-shaped blade (in plan) wrapping one outer corner of the
# jaw body: the blade in front of the shoulder face (beside the nose) is the
# pulling surface, the blade along the jaw side locates the fit.
SHOULDER_X = JAW_X0 + JAW_L            # jaw body outer face
carrier_r = (
    cq.Workplane("XY", origin=((CAR_X0 + CAR_X1) / 2, 0, CAR_Z0))
    .box(CAR_X1 - CAR_X0, CAR_W, CAR_Z1 - CAR_Z0, centered=(True, True, False))
)
for sy in (1, -1):
    y_in = NOSE_W / 2 + 0.5            # clear of the nose
    y_out = JAW_W / 2 + FIT_CLR
    shoulder_blade = (
        cq.Workplane("XY", origin=(SHOULDER_X + FIT_CLR + HOOK_T / 2,
                                   sy * (y_in + y_out) / 2, HOOK_Z0))
        .box(HOOK_T, y_out - y_in, CAR_Z0 - HOOK_Z0 + 0.1,
             centered=(True, True, False))
    )
    side_blade = (
        cq.Workplane("XY", origin=((CAR_X0 + SHOULDER_X + FIT_CLR + HOOK_T) / 2,
                                   sy * (y_out + HOOK_T / 2), HOOK_Z0))
        .box(SHOULDER_X + FIT_CLR + HOOK_T - CAR_X0, HOOK_T,
             CAR_Z0 - HOOK_Z0 + 0.1, centered=(True, True, False))
    )
    carrier_r = carrier_r.union(shoulder_blade).union(side_blade)
# screw hole (tapped; LH on this carrier, RH on the mirrored one)
carrier_r = carrier_r.cut(
    cq.Workplane("YZ", origin=(CAR_X0 - 1, 0, SCREW_Z))
    .circle(SCREW_D / 2)
    .extrude(CAR_X1 - CAR_X0 + 2)
)
# square spine hole (sliding fit on this carrier, press fit on the mirror)
carrier_r = carrier_r.cut(
    cq.Workplane("YZ", origin=(CAR_X0 - 1, SPINE_Y, SCREW_Z))
    .rect(SPINE + 0.2, SPINE + 0.2)
    .extrude(CAR_X1 - CAR_X0 + 2)
)
carrier_l = carrier_r.mirror("YZ")
carrier_l = carrier_l.cut(  # widen mirrored spine hole to nominal (press fit)
    cq.Workplane("YZ", origin=(-CAR_X1 - 1, SPINE_Y, SCREW_Z))
    .rect(SPINE, SPINE)
    .extrude(CAR_X1 - CAR_X0 + 2)
)

# ---- tool: guide spine ------------------------------------------------------
spine = (
    cq.Workplane("YZ", origin=(-30, SPINE_Y, SCREW_Z))
    .rect(SPINE, SPINE)
    .extrude(60)
)

# ---- tool: opposed-thread screw + knob --------------------------------------
screw = (
    cq.Workplane("YZ", origin=(-40, 0, SCREW_Z))
    .circle(SCREW_D / 2)
    .extrude(84)
    .union(  # left retaining cap
        cq.Workplane("YZ", origin=(-43, 0, SCREW_Z)).circle(4).extrude(3)
    )
)
knob = (
    cq.Workplane("YZ", origin=(40, 0, SCREW_Z))
    .polygon(12, 16)
    .extrude(10)
    .edges(">X").chamfer(1.0)
)
screw = screw.union(knob)

# ---- assembly ---------------------------------------------------------------
assy = cq.Assembly(name="fine_screw_loading_tool")
# fixture reference (one jaw pair of the C-frame)
assy.add(floor, name="frame_floor", color=cq.Color(0.35, 0.38, 0.42))
assy.add(bar, name="centre_bar", color=cq.Color(0.68, 0.70, 0.74))
assy.add(jaw_r, name="spring_jaw_right", color=cq.Color(0.92, 0.60, 0.20))
assy.add(jaw_r.mirror("YZ"), name="spring_jaw_left", color=cq.Color(0.92, 0.60, 0.20))
assy.add(blue_jaw_r, name="outer_jaw_right", color=cq.Color(0.30, 0.52, 0.90))
assy.add(blue_jaw_r.mirror("YZ"), name="outer_jaw_left", color=cq.Color(0.30, 0.52, 0.90))
assy.add(sample_r, name="sample_right", color=cq.Color(0.20, 0.75, 0.65))
assy.add(sample_r.mirror("YZ"), name="sample_left", color=cq.Color(0.20, 0.75, 0.65))
assy.add(springs_r, name="springs_right", color=cq.Color(0.95, 0.85, 0.10))
assy.add(springs_r.mirror("YZ"), name="springs_left", color=cq.Color(0.95, 0.85, 0.10))
# loading tool
assy.add(carrier_r, name="tool_carrier_right", color=cq.Color(0.55, 0.25, 0.85))
assy.add(carrier_l, name="tool_carrier_left", color=cq.Color(0.55, 0.25, 0.85))
assy.add(spine, name="tool_guide_spine", color=cq.Color(0.40, 0.18, 0.62))
assy.add(screw, name="tool_screw_and_knob", color=cq.Color(0.20, 0.20, 0.22))

if __name__ == "__main__":
    import os
    out = os.path.dirname(os.path.abspath(__file__))
    step_path = os.path.join(out, "fine_screw_loading_tool.step")
    try:
        assy.export(step_path)
    except AttributeError:
        assy.save(step_path)
    print("wrote", step_path)
