# Three hands-free release concepts for the loading tool - side-by-side study.
#
# The tool still engages the orange jaws with the same form-fitted corner
# hooks. Only the actuation on top changes: instead of turning a fine screw,
# the operator latches the tool with one squeeze ("click") and then releases
# the fixture springs slowly.
#
#   A  RATCHET      pump a lever, teeth click, jaws step open and self-hold;
#                   release lever lets it down one tooth at a time
#   B  TOGGLE       one squeeze goes over dead centre and locks; a rotary
#                   damper on the pivot limits the closing speed
#   C  CLIP+SCREW   the toggle takes the coarse travel, a short fine screw
#                   takes the last couple of mm gently
#
# Geometry is schematic - the point is comparable envelope, part count and
# hand motion, not final detail. All dimensions in mm.

import cadquery as cq

from fine_screw_loading_tool import (
    floor, bar, jaw_r, blue_jaw_r, sample_r, springs_r,
    JAW_X0, JAW_L, JAW_W, NOSE_W, FIT_CLR, HOOK_T, HOOK_Z0,
    CAR_X0, CAR_X1, CAR_W, CAR_Z0, CAR_Z1, GAP_OPEN,
)

STROKE = GAP_OPEN            # inward travel required per side
SHOULDER_X = JAW_X0 + JAW_L

# ---- shared: hook carrier (no screw / spine features) -----------------------
def make_carrier():
    car = (
        cq.Workplane("XY", origin=((CAR_X0 + CAR_X1) / 2, 0, CAR_Z0))
        .box(CAR_X1 - CAR_X0, CAR_W, CAR_Z1 - CAR_Z0, centered=(True, True, False))
    )
    for sy in (1, -1):
        y_in = NOSE_W / 2 + 0.5
        y_out = JAW_W / 2 + FIT_CLR
        shoulder = (
            cq.Workplane("XY", origin=(SHOULDER_X + FIT_CLR + HOOK_T / 2,
                                       sy * (y_in + y_out) / 2, HOOK_Z0))
            .box(HOOK_T, y_out - y_in, CAR_Z0 - HOOK_Z0 + 0.1,
                 centered=(True, True, False))
        )
        side = (
            cq.Workplane("XY", origin=((CAR_X0 + SHOULDER_X + FIT_CLR + HOOK_T) / 2,
                                       sy * (y_out + HOOK_T / 2), HOOK_Z0))
            .box(SHOULDER_X + FIT_CLR + HOOK_T - CAR_X0, HOOK_T,
                 CAR_Z0 - HOOK_Z0 + 0.1, centered=(True, True, False))
        )
        car = car.union(shoulder).union(side)
    return car

# ---- shared: riser posts standing on the carriers ---------------------------
RISER_X0, RISER_X1 = 20.0, 28.0
RISER_W = 14.0
BAR_Z, BAR_H, BAR_YW = 42.0, 8.0, 9.0     # actuation bar cross-section

def make_riser(z_top, slot=False):
    r = (
        cq.Workplane("XY", origin=((RISER_X0 + RISER_X1) / 2, 0, CAR_Z1))
        .box(RISER_X1 - RISER_X0, RISER_W, z_top - CAR_Z1, centered=(True, True, False))
    )
    if slot:   # clearance so the bar slides through this riser
        r = r.cut(
            cq.Workplane("YZ", origin=(RISER_X0 - 1, 0, BAR_Z))
            .rect(BAR_YW + 0.4, BAR_H + 0.4)
            .extrude(RISER_X1 - RISER_X0 + 2)
        )
    return r

def plate(pts, thick, ycentre=0.0):
    """Flat plate from an (X, Z) outline, extruded along Y."""
    w = cq.Workplane("XZ").polyline(pts).close().extrude(thick)
    return w.translate((0, ycentre + thick / 2, 0))

def pin(x, z, d=4.0, length=20.0):
    return (
        cq.Workplane("YZ", origin=(x, -length / 2, z))
        .circle(d / 2).extrude(length)
        .rotate((x, 0, z), (x, 0, z + 1), 0)
    )

def pin_y(x, z, d=4.0, length=20.0):
    return cq.Workplane("XZ", origin=(x, length / 2, z)).circle(d / 2).extrude(length)

# ---- fixture reference (shared by all three) --------------------------------
def add_fixture(assy):
    assy.add(floor, name="frame_floor", color=cq.Color(0.35, 0.38, 0.42))
    assy.add(bar, name="centre_bar", color=cq.Color(0.68, 0.70, 0.74))
    assy.add(jaw_r, name="spring_jaw_right", color=cq.Color(0.92, 0.60, 0.20))
    assy.add(jaw_r.mirror("YZ"), name="spring_jaw_left", color=cq.Color(0.92, 0.60, 0.20))
    assy.add(blue_jaw_r, name="outer_jaw_right", color=cq.Color(0.30, 0.52, 0.90))
    assy.add(blue_jaw_r.mirror("YZ"), name="outer_jaw_left", color=cq.Color(0.30, 0.52, 0.90))
    assy.add(sample_r, name="sample_right", color=cq.Color(0.20, 0.75, 0.65))
    assy.add(sample_r.mirror("YZ"), name="sample_left", color=cq.Color(0.20, 0.75, 0.65))
    assy.add(springs_r, name="spring_right", color=cq.Color(0.95, 0.85, 0.10))
    assy.add(springs_r.mirror("YZ"), name="spring_left", color=cq.Color(0.95, 0.85, 0.10))

PURPLE = cq.Color(0.55, 0.25, 0.85)
DARK = cq.Color(0.20, 0.20, 0.22)
STEEL = cq.Color(0.62, 0.65, 0.70)
ACCENT = cq.Color(0.90, 0.30, 0.30)

# =============================================================================
# CONCEPT A - ratchet + pawl, stepwise release
# =============================================================================
def concept_a():
    carrier_r = make_carrier()
    carrier_l = carrier_r.mirror("YZ")
    riser_r = make_riser(54.0, slot=True)          # tall: carries the mechanism
    riser_l = make_riser(48.0).mirror("YZ")

    # rack bar: fixed in the left riser, sliding through the right one
    rack = (
        cq.Workplane("XY", origin=(-8.0, 0, BAR_Z - BAR_H / 2))
        .box(96.0, BAR_YW, BAR_H, centered=(True, True, False))
    )
    # sawtooth strip on top of the bar, drawn as a single closed outline
    p, n, x0 = 2.0, 30, -18.0
    pts = [(x0, BAR_Z + BAR_H / 2 - 1.0), (x0, BAR_Z + BAR_H / 2 - 0.5)]
    for i in range(n):
        pts.append((x0 + (i + 1) * p, BAR_Z + BAR_H / 2 + 1.4))
        pts.append((x0 + (i + 1) * p, BAR_Z + BAR_H / 2 - 0.5))
    pts.append((x0 + n * p, BAR_Z + BAR_H / 2 - 1.0))
    rack = rack.union(plate(pts, BAR_YW))

    TEETH_Z = BAR_Z + BAR_H / 2 + 1.4
    # squeeze lever, pivoted high on the right riser
    lever = plate([(22, 50), (30, 50), (78, 62), (74, 66), (20, 56)], 5.0, ycentre=5.5)
    # drive pawl hanging from the lever onto the teeth
    drive_pawl = plate([(21, 51), (26, 51), (24, TEETH_Z - 0.2), (20, TEETH_Z - 0.2)],
                       4.0, ycentre=0.5)
    # holding pawl + its release lever (one part), pivoted lower and forward
    hold = plate([(8, 36), (14, 36), (16, TEETH_Z - 0.2), (10, TEETH_Z - 0.2)],
                 4.0, ycentre=-5.0)
    release = plate([(9, 34), (14, 34), (56, 20), (54, 16)], 4.0, ycentre=-5.0)

    assy = cq.Assembly(name="concept_a_ratchet")
    add_fixture(assy)
    assy.add(carrier_r, name="tool_carrier_right", color=PURPLE)
    assy.add(carrier_l, name="tool_carrier_left", color=PURPLE)
    assy.add(riser_r, name="riser_right", color=PURPLE)
    assy.add(riser_l, name="riser_left", color=PURPLE)
    assy.add(rack, name="rack_bar", color=STEEL)
    assy.add(lever, name="squeeze_lever", color=DARK)
    assy.add(drive_pawl, name="drive_pawl", color=DARK)
    assy.add(hold, name="holding_pawl", color=ACCENT)
    assy.add(release, name="release_lever", color=ACCENT)
    assy.add(pin_y(26, 53), name="pin_lever", color=DARK)
    assy.add(pin_y(11, 35), name="pin_pawl", color=DARK)
    return assy

# =============================================================================
# CONCEPT B - over-centre toggle + rotary damper
# =============================================================================
def concept_b():
    carrier_r = make_carrier()
    carrier_l = carrier_r.mirror("YZ")
    riser_r = make_riser(54.0, slot=True)
    riser_l = make_riser(48.0).mirror("YZ")

    guide = (
        cq.Workplane("XY", origin=(-8.0, 0, BAR_Z - BAR_H / 2))
        .box(80.0, BAR_YW, BAR_H, centered=(True, True, False))
    )
    # handle: pivots on the right riser, crank point below the pivot
    handle = plate([(20, 46), (30, 50), (76, 62), (72, 67), (18, 53)], 5.0, ycentre=6.0)
    # toggle link from the handle crank to the left riser pin
    link = plate([(-26, 40), (18, 44), (18, 48), (-26, 44)], 4.0, ycentre=-6.0)
    damper = (
        cq.Workplane("XZ", origin=(26, 13.0, 50)).circle(7.0).extrude(11.0)
    )

    assy = cq.Assembly(name="concept_b_toggle_damper")
    add_fixture(assy)
    assy.add(carrier_r, name="tool_carrier_right", color=PURPLE)
    assy.add(carrier_l, name="tool_carrier_left", color=PURPLE)
    assy.add(riser_r, name="riser_right", color=PURPLE)
    assy.add(riser_l, name="riser_left", color=PURPLE)
    assy.add(guide, name="guide_bar", color=STEEL)
    assy.add(handle, name="toggle_handle", color=DARK)
    assy.add(link, name="toggle_link", color=ACCENT)
    assy.add(damper, name="rotary_damper", color=cq.Color(0.20, 0.75, 0.65))
    assy.add(pin_y(26, 50), name="pin_handle", color=DARK)
    assy.add(pin_y(-24, 42), name="pin_link", color=DARK)
    return assy

# =============================================================================
# CONCEPT C - toggle clip for coarse travel + fine screw for the last mm
# =============================================================================
def concept_c():
    carrier_r = make_carrier()
    carrier_l = carrier_r.mirror("YZ")
    riser_r = make_riser(54.0, slot=True)
    riser_l = make_riser(48.0).mirror("YZ")

    guide = (
        cq.Workplane("XY", origin=(-8.0, 0, BAR_Z - BAR_H / 2))
        .box(80.0, BAR_YW, BAR_H, centered=(True, True, False))
    )
    handle = plate([(20, 46), (30, 50), (76, 62), (72, 67), (18, 53)], 5.0, ycentre=6.0)
    # link stops short of the left riser; a fine screw closes the gap
    link = plate([(-14, 40), (18, 44), (18, 48), (-14, 44)], 4.0, ycentre=-6.0)
    screw = (
        cq.Workplane("YZ", origin=(-34.0, -6.0, 42.0))
        .circle(2.5).extrude(22.0)
    )
    knob = (
        cq.Workplane("YZ", origin=(-44.0, -6.0, 42.0))
        .polygon(12, 15).extrude(9.0)
        .edges("<X").chamfer(1.0)
    )

    assy = cq.Assembly(name="concept_c_clip_plus_screw")
    add_fixture(assy)
    assy.add(carrier_r, name="tool_carrier_right", color=PURPLE)
    assy.add(carrier_l, name="tool_carrier_left", color=PURPLE)
    assy.add(riser_r, name="riser_right", color=PURPLE)
    assy.add(riser_l, name="riser_left", color=PURPLE)
    assy.add(guide, name="guide_bar", color=STEEL)
    assy.add(handle, name="toggle_handle", color=DARK)
    assy.add(link, name="toggle_link", color=ACCENT)
    assy.add(screw, name="fine_release_screw", color=DARK)
    assy.add(knob, name="fine_release_knob", color=DARK)
    assy.add(pin_y(26, 50), name="pin_handle", color=DARK)
    return assy

CONCEPTS = {
    "concept_a_ratchet": concept_a,
    "concept_b_toggle_damper": concept_b,
    "concept_c_clip_plus_screw": concept_c,
}

if __name__ == "__main__":
    import os
    out = os.path.dirname(os.path.abspath(__file__))
    for name, fn in CONCEPTS.items():
        a = fn()
        path = os.path.join(out, name + ".step")
        try:
            a.export(path)
        except AttributeError:
            a.save(path)
        bb = a.toCompound().BoundingBox()
        tool_parts = [c.name for c in a.children
                      if not c.name.startswith(("frame_", "centre_", "spring_jaw",
                                                "outer_jaw", "sample_", "spring_"))]
        print(f"{name}: {len(tool_parts)} tool parts, "
              f"envelope {bb.xlen:.0f} x {bb.ylen:.0f} x {bb.zlen:.0f} mm")
