# Tweezer version of the loading tool - two parts, no pins, no linkage.
#
# The big simplification: the tool does not need to HOOK the orange jaws at
# all. It only needs to push them inward, and two jaws pushed inward from
# outside is exactly what a pair of tweezers does. So the wrap-around pockets,
# the parallelogram links, the pins and the toggle all disappear:
#
#   part 1  a sprung tweezer, forked at each tip so the prongs straddle the
#           jaw nose and bear on the two shoulder faces beside it (the same
#           four engagement spots as before, now as simple push faces)
#   part 2  a sliding lock ring
#
# Squeeze -> the jaws move inward and both sample gaps open. Slide the ring
# down the taper -> it holds that opening, hands free. Slide the ring back
# slowly -> the fixture springs let the jaws close at exactly the speed your
# thumb allows. That is the controlled release, with no damper, no pawl and
# no thread: the ring IS the latch and the release valve.
#
# Because the tips only push on flat faces, jaw tilt no longer matters - the
# reason the plier needed parallelogram links was the deep form-fitted pocket,
# and there isn't one any more. A few degrees of arm flex is harmless.
#
# A small flange on the outside of each prong hugs the jaw's side face, so the
# tool still drops into place with a definite located feel rather than
# floating on the shoulder faces.
#
# Everything scales with the fixture: unlike a linkage, a sprung blade has no
# minimum feature size, so if the real jaws are smaller the whole tool shrinks
# with them. Dimensions in mm.

import cadquery as cq

from release_concepts import add_fixture, PURPLE, STEEL
from fine_screw_loading_tool import JAW_X0, JAW_L, JAW_W, JAW_H, NOSE_W

# ---- what the fixture dictates ----------------------------------------------
SHOULDER_X = JAW_X0 + JAW_L        # the face each prong pushes on
PRONG_Y0 = NOSE_W / 2 + 0.3        # inboard edge, clear of the nose
PRONG_Y1 = JAW_W / 2 - 0.2         # outboard edge, on the shoulder
NOTCH_Y = NOSE_W / 2 + 0.3         # half-width of the slot that clears the nose

# ---- tweezer proportions -----------------------------------------------------
BLADE_T = 0.8                      # spring thickness (bends in X)
TIP_W, MID_W, TOP_W = JAW_W - 0.4, 5.0, 3.5            # blade width in Y
TIP_Z0, TIP_Z1 = 1.2, 13.0         # straight tip section
KNEE = (6.0, 44.0)                 # where the taper eases off
TAIL = (1.2, 68.0)
TAIL_Z1 = 78.0

RING_Z0, RING_Z1 = 36.0, 41.0
FLANGE_T = 0.6                     # side flange that locates the tool in Y


def bar_plate(p0, p1, w, t, y=0.0):
    """Flat bar between two (X, Z) points: w across the XZ plane, t along Y."""
    import math
    dx, dz = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dz)
    px, pz = -dz / L, dx / L
    pts = [
        (p0[0] + px * w / 2, p0[1] + pz * w / 2),
        (p1[0] + px * w / 2, p1[1] + pz * w / 2),
        (p1[0] - px * w / 2, p1[1] - pz * w / 2),
        (p0[0] - px * w / 2, p0[1] - pz * w / 2),
    ]
    wp = cq.Workplane("XZ").polyline(pts).close().extrude(t)
    return wp.translate((0, y + t / 2, 0))


# ---- one arm: straight tip, tapering shank, forked at the bottom ------------
def make_arm():
    axis_x = SHOULDER_X + BLADE_T / 2          # inner face lands on the shoulder
    arm = (
        bar_plate((axis_x, TIP_Z0), (axis_x, TIP_Z1), BLADE_T, TIP_W)
        .union(bar_plate((axis_x, TIP_Z1), KNEE, BLADE_T, MID_W))
        .union(bar_plate(KNEE, TAIL, BLADE_T, TOP_W))
    )
    # slot that clears the jaw nose, turning the tip into two prongs
    arm = arm.cut(
        cq.Workplane("XY", origin=(SHOULDER_X + 2.0, 0, TIP_Z0 - 1.0))
        .box(6.0, 2 * NOTCH_Y, TIP_Z1 - TIP_Z0, centered=(True, True, False))
    )
    # locating flanges hugging the outside of the jaw
    for sy in (1, -1):
        arm = arm.union(
            cq.Workplane("XY", origin=(SHOULDER_X - 1.4,
                                       sy * (JAW_W / 2 + 0.12 + FLANGE_T / 2),
                                       TIP_Z0))
            .box(3.0 + BLADE_T, FLANGE_T, 5.0, centered=(True, True, False))
        )
    return arm


arm_r = make_arm()
arm_l = arm_r.mirror("YZ")
tail = (
    cq.Workplane("XY", origin=(0, 0, TAIL[1] - 2.0))
    .box(2 * TAIL[0] + BLADE_T, TOP_W, TAIL_Z1 - TAIL[1] + 2.0,
         centered=(True, True, False))
)
tweezer = arm_r.union(arm_l).union(tail)

# ---- sliding lock ring -------------------------------------------------------
def ring_opening_half_x(z):
    """Outer half-span of the two arms at height z, on the tapering shank."""
    f = (z - TIP_Z1) / (KNEE[1] - TIP_Z1)
    centre = (SHOULDER_X + BLADE_T / 2) + f * (KNEE[0] - (SHOULDER_X + BLADE_T / 2))
    return centre + BLADE_T / 2


# the arms are widest at the ring's lower edge, so that is what sizes the bore;
# the ring bears on that edge and the taper does the wedging
_half = ring_opening_half_x(RING_Z0) + 0.15
ring = (
    cq.Workplane("XY", origin=(0, 0, RING_Z0))
    .box(2 * _half + 3.0, MID_W + 3.0, RING_Z1 - RING_Z0, centered=(True, True, False))
    .cut(
        cq.Workplane("XY", origin=(0, 0, RING_Z0 - 1.0))
        .box(2 * _half, MID_W + 0.6, RING_Z1 - RING_Z0 + 2.0,
             centered=(True, True, False))
    )
)

# ---- assembly ----------------------------------------------------------------
assy = cq.Assembly(name="tweezer_loading_tool")
add_fixture(assy)
assy.add(tweezer, name="tweezer_body", color=PURPLE)
assy.add(ring, name="lock_ring", color=STEEL)

if __name__ == "__main__":
    import os
    out = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(out, "tweezer_tool.step")
    try:
        assy.export(path)
    except AttributeError:
        assy.save(path)
    tool = cq.Compound.makeCompound([tweezer.val(), ring.val()])
    bb = tool.BoundingBox()
    print("wrote", path)
    print(f"tool alone: X {bb.xlen:.0f} x Y {bb.ylen:.0f} x Z {bb.zlen:.0f} mm, 2 parts")
    print(f"prong contact: x = +/-{SHOULDER_X:.0f}, y = +/-{PRONG_Y0:.1f}..{PRONG_Y1:.1f}")
    print(f"blade {BLADE_T} mm thick - spring force is set by this alone")
