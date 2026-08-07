# Four-Point Fitted Hook Tool - Controlled Release (concept CAD)
#
# Parametric model of the two-jaw centering fixture: a fine-pitch screw with
# opposed (LH/RH) threads drives two orange nut blocks inward by equal amounts;
# each block carries a purple hook carrier whose two fitted shoes engage
# dedicated grooves on the block faces (4 engagement points total). Two 7x7 mm
# samples are clamped between the block inner faces and a central datum plate.
#
# Improvements over the sketch:
#   - base plate with a guide rib + matching groove under each block, so screw
#     torque cannot rotate the blocks and travel stays straight
#   - shoe engagement defined as chamfered grooves for repeatable 4-point fit
#   - preload springs on both sides to remove opposed-thread backlash during
#     slow reverse release
#   - thrust washers, screw clearance hole through the datum plate, 12-flat knob
#
# Threads are intentionally not modeled (cosmetic in STEP); recommended spec:
# M8x0.75, RH on one half / LH on the other. All dimensions in mm.

import cadquery as cq

# ---- parameters -------------------------------------------------------------
SAMPLE = 7.0            # sample square cross-section
SAMPLE_LEN = 25.0
PLATE_T = 3.0           # central datum plate thickness
SCREW_D = 8.0
SCREW_Z = 30.0          # screw axis height

BASE_L, BASE_W, BASE_T = 150.0, 60.0, 8.0
RIB_W, RIB_H = 10.0, 5.0
CLR = 0.2               # sliding clearance

BLOCK_L, BLOCK_W = 30.0, 40.0          # X x Y
BLOCK_TOP = 43.0                       # block spans z: BASE_T .. BLOCK_TOP
GROOVE_Z0, GROOVE_Z1 = 32.0, 38.0      # shoe groove on block faces
GROOVE_DEPTH, GROOVE_L = 4.0, 18.0

INNER_X = PLATE_T / 2 + SAMPLE         # closed-on-sample inner face position

BRACKET_X0, BRACKET_X1 = 60.0, 72.0
BRACKET_H = 45.0

# ---- base plate with guide rib ---------------------------------------------
base = (
    cq.Workplane("XY")
    .box(BASE_L, BASE_W, BASE_T, centered=(True, True, False))
    .union(
        cq.Workplane("XY", origin=(0, 0, BASE_T))
        .box(BASE_L, RIB_W, RIB_H, centered=(True, True, False))
    )
)

def rib_notch(x0, x1):
    """Clearance cutter for parts that sit on the base and straddle the rib."""
    return (
        cq.Workplane("XY", origin=((x0 + x1) / 2, 0, BASE_T))
        .box(abs(x1 - x0) + 1, RIB_W + 2 * CLR, RIB_H + CLR, centered=(True, True, False))
    )

# ---- end bracket (right; left is mirrored) ----------------------------------
bracket_r = (
    cq.Workplane("XY", origin=((BRACKET_X0 + BRACKET_X1) / 2, 0, BASE_T))
    .box(BRACKET_X1 - BRACKET_X0, BASE_W, BRACKET_H, centered=(True, True, False))
    .cut(rib_notch(BRACKET_X0, BRACKET_X1))
    .cut(
        cq.Workplane("YZ", origin=(BRACKET_X0 - 1, 0, SCREW_Z))
        .circle((SCREW_D + 2) / 2)
        .extrude(BRACKET_X1 - BRACKET_X0 + 2)
    )
)
bracket_l = bracket_r.mirror("YZ")

# ---- moving nut block (orange, right) ---------------------------------------
block_x0, block_x1 = INNER_X, INNER_X + BLOCK_L
block_r = (
    cq.Workplane("XY", origin=((block_x0 + block_x1) / 2, 0, BASE_T))
    .box(BLOCK_L, BLOCK_W, BLOCK_TOP - BASE_T, centered=(True, True, False))
    .cut(rib_notch(block_x0, block_x1))
)
# tapped screw hole (LH on this side, RH on the mirrored side)
block_r = block_r.cut(
    cq.Workplane("YZ", origin=(block_x0 - 1, 0, SCREW_Z))
    .circle(SCREW_D / 2)
    .extrude(BLOCK_L + 2)
)
# shoe engagement grooves on front/back faces, chamfered lead-in via cutter
for sign in (1, -1):
    cutter = (
        cq.Workplane("XY", origin=((block_x0 + block_x1) / 2,
                                   sign * (BLOCK_W / 2 - GROOVE_DEPTH / 2),
                                   GROOVE_Z0))
        .box(GROOVE_L, GROOVE_DEPTH, GROOVE_Z1 - GROOVE_Z0, centered=(True, True, False))
    )
    block_r = block_r.cut(cutter)
block_r = block_r.edges("|Y and >Z").chamfer(1.0)

# ---- fitted hook carrier (purple, right) ------------------------------------
car_x0, car_x1 = block_x0 + 3, block_x1 + 5
carrier_r = (
    cq.Workplane("XY", origin=((car_x0 + car_x1) / 2, 0, BLOCK_TOP))
    .box(car_x1 - car_x0, BLOCK_W + 8, 6, centered=(True, True, False))
)
# wedge grip on top (rises toward the outer side)
wedge = (
    cq.Workplane("XZ", origin=(0, 0, 0))
    .polyline([(car_x0 + 2, BLOCK_TOP + 6), (car_x1 - 2, BLOCK_TOP + 6),
               (car_x1 - 2, BLOCK_TOP + 15)])
    .close()
    .extrude(16, both=True)
)
carrier_r = carrier_r.union(wedge)
# two legs with fitted shoes (lips) that drop into the block grooves
leg_x0 = (block_x0 + block_x1) / 2 - (GROOVE_L - 4) / 2
leg_w = GROOVE_L - 4
for sign in (1, -1):
    leg = (
        cq.Workplane("XY", origin=(leg_x0 + leg_w / 2,
                                   sign * (BLOCK_W / 2 + 2), GROOVE_Z0 - 1))
        .box(leg_w, 4, BLOCK_TOP + 6 - (GROOVE_Z0 - 1), centered=(True, True, False))
    )
    lip = (
        cq.Workplane("XY", origin=(leg_x0 + leg_w / 2,
                                   sign * (BLOCK_W / 2 - (GROOVE_DEPTH - CLR) / 2),
                                   GROOVE_Z0 + CLR))
        .box(leg_w, GROOVE_DEPTH - CLR, GROOVE_Z1 - GROOVE_Z0 - 2 * CLR,
             centered=(True, True, False))
        .edges("<Z").chamfer(0.8)
    )
    carrier_r = carrier_r.union(leg).union(lip)

# ---- central datum plate (fixed, gray) --------------------------------------
center_plate = (
    cq.Workplane("XY", origin=(0, 0, BASE_T))
    .box(PLATE_T, BLOCK_W, 42, centered=(True, True, False))
    .cut(rib_notch(-PLATE_T, PLATE_T))
    .cut(
        cq.Workplane("YZ", origin=(-PLATE_T, 0, SCREW_Z))
        .circle(SCREW_D / 2 + 0.5)
        .extrude(2 * PLATE_T)
    )
)

# ---- screw + knob -----------------------------------------------------------
knob_x = 74.0
screw = (
    cq.Workplane("YZ", origin=(-77, 0, SCREW_Z))
    .circle(SCREW_D / 2)
    .extrude(knob_x + 77)
    .union(  # left retaining cap
        cq.Workplane("YZ", origin=(-80, 0, SCREW_Z)).circle(6).extrude(3)
    )
    .union(  # knob collar
        cq.Workplane("YZ", origin=(knob_x - 2, 0, SCREW_Z)).circle(7).extrude(2)
    )
)
knob = (
    cq.Workplane("YZ", origin=(knob_x, 0, SCREW_Z))
    .polygon(12, 26)
    .extrude(14)
    .edges("%CIRCLE" if False else ">X").chamfer(1.5)
)
screw = screw.union(knob)

# ---- thrust washer + preload spring (right) ---------------------------------
washer_r = (
    cq.Workplane("YZ", origin=(block_x1, 0, SCREW_Z))
    .circle(8).circle(SCREW_D / 2 + 0.25)
    .extrude(2)
)

def make_spring(x_start, length, radius=7.0, wire_r=0.8, turns=6):
    try:
        pitch = length / turns
        helix = cq.Wire.makeHelix(pitch, length, radius)
        spring = (
            cq.Workplane("XZ")
            .center(radius, 0)
            .circle(wire_r)
            .sweep(cq.Workplane("XY").newObject([helix]), isFrenet=True)
        )
    except Exception:
        # fallback: simple tube placeholder
        spring = (
            cq.Workplane("XY")
            .circle(radius + wire_r).circle(radius - wire_r)
            .extrude(length)
        )
    return (
        spring.rotate((0, 0, 0), (0, 1, 0), 90)
        .translate((x_start, 0, SCREW_Z))
    )

spring_start = block_x1 + 2 + 1.0            # clear of the thrust washer
spring_r = make_spring(spring_start, BRACKET_X0 - spring_start - 1.5)

# ---- samples (two 7x7 mm) ---------------------------------------------------
sample_r = (
    cq.Workplane("XY", origin=(PLATE_T / 2 + SAMPLE / 2, 0, 20))
    .box(SAMPLE, SAMPLE, SAMPLE_LEN, centered=(True, True, False))
)

# ---- assembly ---------------------------------------------------------------
assy = cq.Assembly(name="four_point_fitted_hook_tool")
assy.add(base, name="base_plate", color=cq.Color(0.62, 0.65, 0.70))
assy.add(bracket_l, name="bracket_left", color=cq.Color(0.30, 0.52, 0.90))
assy.add(bracket_r, name="bracket_right", color=cq.Color(0.30, 0.52, 0.90))
assy.add(center_plate, name="center_datum_plate", color=cq.Color(0.75, 0.77, 0.80))
assy.add(block_r, name="nut_block_right", color=cq.Color(0.92, 0.60, 0.20))
assy.add(block_r.mirror("YZ"), name="nut_block_left", color=cq.Color(0.92, 0.60, 0.20))
assy.add(carrier_r, name="hook_carrier_right", color=cq.Color(0.55, 0.25, 0.85))
assy.add(carrier_r.mirror("YZ"), name="hook_carrier_left", color=cq.Color(0.55, 0.25, 0.85))
assy.add(screw, name="screw_and_knob", color=cq.Color(0.20, 0.20, 0.22))
assy.add(washer_r, name="thrust_washer_right", color=cq.Color(0.20, 0.75, 0.65))
assy.add(washer_r.mirror("YZ"), name="thrust_washer_left", color=cq.Color(0.20, 0.75, 0.65))
assy.add(spring_r, name="preload_spring_right", color=cq.Color(0.95, 0.85, 0.10))
assy.add(spring_r.mirror("YZ"), name="preload_spring_left", color=cq.Color(0.95, 0.85, 0.10))
assy.add(sample_r, name="sample_right", color=cq.Color(0.45, 0.80, 0.45))
assy.add(sample_r.mirror("YZ"), name="sample_left", color=cq.Color(0.45, 0.80, 0.45))

if __name__ == "__main__":
    import os
    out = os.path.dirname(os.path.abspath(__file__))
    step_path = os.path.join(out, "four_point_hook_tool.step")
    try:
        assy.export(step_path)
    except AttributeError:
        assy.save(step_path)
    print("wrote", step_path)

    try:
        comp = assy.toCompound()
        cq.exporters.export(
            cq.Workplane(obj=comp),
            os.path.join(out, "preview.svg"),
            opt={
                "width": 1200, "height": 800, "marginLeft": 40, "marginTop": 40,
                "projectionDir": (1.0, -1.2, 0.8),
                "showAxes": False, "showHidden": False,
                "strokeWidth": 0.8,
            },
        )
        print("wrote preview.svg")
    except Exception as e:
        print("preview skipped:", e)
