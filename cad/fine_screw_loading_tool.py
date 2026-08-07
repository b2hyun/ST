# Fine-Screw Loading Tool + spring-jaw fixture pair (concept CAD)
#
# Context: the fixture is a C-frame with a fixed centre bar. On each side an
# orange jaw is pushed OUTWARD by springs, clamping a 7x7 mm sample between the
# jaw nose and the outer blue jaw. The purple loading tool sits on top of one
# jaw pair: its downward pins drop into engagement sockets on the orange jaws,
# and a fine-pitch screw with opposed (LH/RH) threads pulls both jaws inward,
# compressing the springs and opening both sample gaps. Reversing the screw
# slowly releases the springs so the samples are clamped gently.
#
# The model is positioned in the ENGAGED state: jaws pulled inward, springs
# compressed, both sample gaps open with samples inserted.
#
# Improvements over the sketch:
#   - two pins per carrier (4 total) so screw torque cannot rotate the tool
#   - square guide spine between the carriers keeps the pins aligned while
#     the tool is handled and carries the screw torque reaction
#   - chamfered pin tips + 0.1 mm radial socket clearance for easy drop-in
#   - 12-flat knob for controlled slow release
#
# Threads are not modeled (cosmetic in STEP); recommended: M5x0.5, RH on one
# screw half / LH on the other. All dimensions in mm, parametric guesses
# scaled from the 7x7 mm sample - real jaw dimensions require measurement.

import cadquery as cq

# ---- fixture parameters (X = clamp axis, Y = along centre bar, Z = up) ------
SAMPLE = 7.0
SAMPLE_T = 7.0            # sample thickness along clamp axis
BAR_HALF = 4.0            # centre bar half-thickness
BAR_H = 25.0
SPRING_GAP = 6.0          # bar-to-jaw gap in compressed (engaged) state
JAW_X0 = BAR_HALF + SPRING_GAP          # orange jaw inner face
JAW_L, JAW_W, JAW_H = 16.0, 24.0, 20.0  # orange jaw body
NOSE_L, NOSE_W = 8.0, 10.0              # jaw nose toward the sample
GAP_OPEN = 8.0            # open sample gap (sample 7 + 1 clearance)
BLUE_X0 = JAW_X0 + JAW_L + NOSE_L + GAP_OPEN
SOCKET_D, SOCKET_DEPTH = 4.2, 6.0
SOCKET_X = JAW_X0 + JAW_L / 2           # socket centre over jaw body
SOCKET_Y = 8.0                          # sockets at y = +/- SOCKET_Y

# ---- tool parameters --------------------------------------------------------
PIN_D = 4.0
CAR_X0, CAR_X1 = 8.0, 28.0    # right carrier footprint
CAR_W, CAR_Z0, CAR_Z1 = 30.0, 20.5, 34.0
SCREW_D, SCREW_Z = 5.0, 29.0
SPINE, SPINE_Y = 6.0, 10.0    # square guide spine, offset from screw axis

# ---- fixture: floor + centre bar --------------------------------------------
floor = (
    cq.Workplane("XY", origin=(0, 0, -4))
    .box(120, 70, 4, centered=(True, True, False))
)
bar = cq.Workplane("XY").box(2 * BAR_HALF, 60, BAR_H, centered=(True, True, False))

# ---- fixture: orange spring jaw (right; left mirrored) ----------------------
jaw_r = (
    cq.Workplane("XY", origin=(JAW_X0 + JAW_L / 2, 0, 0))
    .box(JAW_L, JAW_W, JAW_H, centered=(True, True, False))
    .union(
        cq.Workplane("XY", origin=(JAW_X0 + JAW_L + NOSE_L / 2, 0, 0))
        .box(NOSE_L, NOSE_W, JAW_H, centered=(True, True, False))
    )
)
for sy in (1, -1):  # engagement sockets for the tool pins
    jaw_r = jaw_r.cut(
        cq.Workplane("XY", origin=(SOCKET_X, sy * SOCKET_Y, JAW_H - SOCKET_DEPTH))
        .circle(SOCKET_D / 2)
        .extrude(SOCKET_DEPTH + 1)
    )

# ---- fixture: blue outer jaw + sample ---------------------------------------
blue_jaw_r = (
    cq.Workplane("XY", origin=(BLUE_X0 + 6, 0, 0))
    .box(12, JAW_W, 18, centered=(True, True, False))
)
sample_r = (
    cq.Workplane("XY", origin=(BLUE_X0 - GAP_OPEN / 2, 0, 0))
    .box(SAMPLE_T, SAMPLE, SAMPLE, centered=(True, True, False))
)

# ---- fixture: compressed springs (2 per side) -------------------------------
def make_spring(x_start, length, radius=2.5, wire_r=0.6, turns=5, y=0.0, z=10.0):
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
_s0 = BAR_HALF + 0.6 + 0.1
_slen = SPRING_GAP - 2 * (0.6 + 0.1)
springs_r = make_spring(_s0, _slen, y=SOCKET_Y).union(make_spring(_s0, _slen, y=-SOCKET_Y))

# ---- tool: carriers with downward pins --------------------------------------
carrier_r = (
    cq.Workplane("XY", origin=((CAR_X0 + CAR_X1) / 2, 0, CAR_Z0))
    .box(CAR_X1 - CAR_X0, CAR_W, CAR_Z1 - CAR_Z0, centered=(True, True, False))
)
for sy in (1, -1):
    pin = (
        cq.Workplane("XY", origin=(SOCKET_X, sy * SOCKET_Y, JAW_H - 5.0))
        .circle(PIN_D / 2)
        .extrude(CAR_Z0 - (JAW_H - 5.0))
        .faces("<Z").chamfer(0.8)
    )
    carrier_r = carrier_r.union(pin)
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
