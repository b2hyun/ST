# Parallel-jaw locking plier version of the loading tool (concept CAD).
#
# Same job as the bar-clamp concepts, different topology: a hand tool you
# squeeze. The two hook carriers ARE the plier jaws - squeezing the handles
# pulls them together, which drags both orange fixture jaws inward, compresses
# the springs and opens both sample gaps. The tool floats on the fixture, so
# the two equal springs balance it and both jaws move inward by themselves.
#
# Why the jaws must stay PARALLEL, not pivot like ordinary pliers:
# the hooks need 8 mm of inward travel per side. On a plain pivoted arm of
# ~40 mm that is roughly 23 deg of jaw rotation, which would cam the flat
# hook pockets straight off the jaw corners and bind the fixture's linear
# guide. So each carrier hangs from the body on a pair of equal-length links
# (a parallelogram): the carrier translates along X and never changes angle.
# The residual arc drop is 40 - sqrt(40^2 - 8^2) = 0.8 mm, and it is taken up
# harmlessly because the hook faces it slides on are vertical.
#
# Locking and slow release follow the vise-grip principle, which is the same
# load-transfer trick as concept C:
#   squeeze -> toggle goes over dead centre and latches (click), hands free
#   -> insert samples -> back the adjusting knob off a few turns so the jaws
#   settle onto the samples under control -> the toggle is now slack, so
#   unlatching it releases nothing and the tool lifts straight out.
#
# Geometry is schematic - link lengths and pivot positions are placeholders
# until the orange jaw and spring free length are measured. Dimensions in mm.

import math
import cadquery as cq

from release_concepts import make_carrier, plate, add_fixture, PURPLE, DARK, STEEL, ACCENT
from fine_screw_loading_tool import CAR_X0, CAR_X1, CAR_Z1

# ---- layout parameters (all in the XZ plane; Y is the tool thickness) -------
TAB_Z1, TAB_YW = 44.0, 30.0   # pin tab added on top of each carrier
PIN_LOW_Z = 40.0              # parallelogram lower pins, on the carrier
PIN_LOW_X = (12.0, 26.0)      # right carrier: front / rear link pins
DRIVE_LOW_X = 19.0            # drive-link pin, between the two

LINK_LEN = 40.0               # parallelogram link length
SHIFT = 8.0                   # inward travel already taken up in this pose
SWING = math.degrees(math.asin(SHIFT / LINK_LEN))            # 11.5 deg
PIN_UP_Z = PIN_LOW_Z + math.sqrt(LINK_LEN ** 2 - SHIFT ** 2)  # ~79.2
ARC_DROP = LINK_LEN - math.sqrt(LINK_LEN ** 2 - SHIFT ** 2)

BODY_Z0, BODY_Z1 = 74.0, 90.0
BODY_HALF_X, BODY_YW = 42.0, 14.0

PIVOT = (0.0, 104.0)          # crossed-handle pivot
HANDLE_TOP_R = (46.0, 170.0)
LOWER_ARM_R = (-19.0, 84.0)   # right handle reaches across to the LEFT carrier

# Y planes: links on centre, drive links next out, handles outermost.
PLANE_Y, DRIVE_Y, HANDLE_Y = 0.0, 10.0, 16.0
LINK_W, LINK_T, SLOT_CLR = 7.0, 6.0, 0.3
DRIVE_W, DRIVE_T = 7.0, 5.0


def bar_plate(p0, p1, w, t, y):
    """Flat bar between two (X, Z) points, thickness t along Y, centred at y."""
    dx, dz = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dz)
    px, pz = -dz / L, dx / L
    pts = [
        (p0[0] + px * w / 2, p0[1] + pz * w / 2),
        (p1[0] + px * w / 2, p1[1] + pz * w / 2),
        (p1[0] - px * w / 2, p1[1] - pz * w / 2),
        (p0[0] - px * w / 2, p0[1] - pz * w / 2),
    ]
    return plate(pts, t, y)


def swept(shape, centre, half_range=SWING + 1.0, steps=5):
    """Union of `shape` rotated about a Y axis through `centre`, for slotting."""
    out = None
    for i in range(steps):
        a = -half_range + 2 * half_range * i / (steps - 1)
        r = shape.rotate((centre[0], -1, centre[1]), (centre[0], 1, centre[1]), a)
        out = r if out is None else out.union(r)
    return out


def pin(x, z, d=4.0, length=30.0):
    return cq.Workplane("XZ", origin=(x, length / 2, z)).circle(d / 2).extrude(length)


# ---- carrier with a pin tab on top ------------------------------------------
carrier_r = make_carrier().union(
    cq.Workplane("XY", origin=((CAR_X0 + CAR_X1) / 2 + 1.0, 0, CAR_Z1))
    .box(CAR_X1 - CAR_X0 - 2, TAB_YW, TAB_Z1 - CAR_Z1, centered=(True, True, False))
)

# ---- body bridge + pivot cheeks ---------------------------------------------
body = (
    cq.Workplane("XY", origin=(0, 0, BODY_Z0))
    .box(2 * BODY_HALF_X, BODY_YW, BODY_Z1 - BODY_Z0, centered=(True, True, False))
    .union(
        cq.Workplane("XY", origin=(0, 0, BODY_Z1))
        .box(26.0, BODY_YW, PIVOT[1] + 5.0 - BODY_Z1, centered=(True, True, False))
    )
)

# ---- parallelogram links, swinging in slots cut through body and tab --------
links = body_slots = tab_slots_r = None
for xl in PIN_LOW_X:
    for sgn in (1, -1):
        lo, up = (sgn * xl, PIN_LOW_Z), (sgn * (xl + SHIFT), PIN_UP_Z)
        lk = bar_plate(lo, up, LINK_W, LINK_T, PLANE_Y)
        links = lk if links is None else links.union(lk)

        fat = bar_plate(lo, up, LINK_W + 2 * SLOT_CLR, LINK_T + 2 * SLOT_CLR, PLANE_Y)
        s_up = swept(fat, up)
        body_slots = s_up if body_slots is None else body_slots.union(s_up)
        if sgn == 1:
            s_lo = swept(fat, lo)
            tab_slots_r = s_lo if tab_slots_r is None else tab_slots_r.union(s_lo)

body = body.cut(body_slots)
carrier_r = carrier_r.cut(tab_slots_r)
carrier_l = carrier_r.mirror("YZ")     # parallelogram slots are on centre, so
                                       # they survive the mirror unchanged

# ---- crossed handles ---------------------------------------------------------
# Each handle sits on its own Y plane and reaches ACROSS the pivot, so the two
# never share material: right handle (+Y) drives the LEFT carrier, and the
# left handle (-Y) drives the RIGHT one. Squeezing the tops together therefore
# converges both jaws - ordinary tongs action.
HANDLE_TOP_L = (-HANDLE_TOP_R[0], HANDLE_TOP_R[1])
LOWER_ARM_L = (-LOWER_ARM_R[0], LOWER_ARM_R[1])

handle_r = (
    bar_plate(PIVOT, HANDLE_TOP_R, 10.0, 5.0, HANDLE_Y)
    .union(bar_plate(PIVOT, LOWER_ARM_R, 9.0, 5.0, HANDLE_Y))
)
handle_l = (
    bar_plate(PIVOT, HANDLE_TOP_L, 10.0, 5.0, -HANDLE_Y)
    .union(bar_plate(PIVOT, LOWER_ARM_L, 9.0, 5.0, -HANDLE_Y))
)

# ---- drive links, each on the plane of the handle that drives it ------------
drive_l = bar_plate(LOWER_ARM_R, (-DRIVE_LOW_X, PIN_LOW_Z), DRIVE_W, DRIVE_T, DRIVE_Y)
drive_r = bar_plate(LOWER_ARM_L, (DRIVE_LOW_X, PIN_LOW_Z), DRIVE_W, DRIVE_T, -DRIVE_Y)

for _car_side, _lo, _y in ((None, (DRIVE_LOW_X, PIN_LOW_Z), -DRIVE_Y),
                           (None, (-DRIVE_LOW_X, PIN_LOW_Z), DRIVE_Y)):
    _arm = LOWER_ARM_L if _lo[0] > 0 else LOWER_ARM_R
    _fat = bar_plate(_arm, _lo, DRIVE_W + 2 * SLOT_CLR, DRIVE_T + 2 * SLOT_CLR, _y)
    _cut = swept(_fat, _lo)
    if _lo[0] > 0:
        carrier_r = carrier_r.cut(_cut)
    else:
        carrier_l = carrier_l.cut(_cut)

# ---- over-centre lock: toggle link + adjusting knob + release lever ---------
KNOB_AT = (-40.0, 158.0)
lock_link = bar_plate((-34.0, 154.0), (14.0, 132.0), 8.0, 7.0, PLANE_Y)
knob = (
    cq.Workplane("XZ", origin=(KNOB_AT[0], 7.0, KNOB_AT[1])).polygon(12, 17.0).extrude(14.0)
)
release = bar_plate((16.0, 124.0), (40.0, 106.0), 7.0, 4.0, -HANDLE_Y - 6.0)

# ---- assembly ----------------------------------------------------------------
assy = cq.Assembly(name="parallel_jaw_locking_plier")
add_fixture(assy)
assy.add(carrier_r, name="jaw_carrier_right", color=PURPLE)
assy.add(carrier_l, name="jaw_carrier_left", color=PURPLE)
assy.add(body, name="body_bridge", color=PURPLE)
assy.add(links, name="parallelogram_links", color=STEEL)
assy.add(handle_r, name="handle_right", color=DARK)
assy.add(handle_l, name="handle_left", color=DARK)
assy.add(drive_r, name="drive_link_right", color=STEEL)
assy.add(drive_l, name="drive_link_left", color=STEEL)
assy.add(lock_link, name="lock_toggle_link", color=ACCENT)
assy.add(knob, name="adjusting_knob", color=ACCENT)
assy.add(release, name="release_lever", color=ACCENT)
for xl in PIN_LOW_X:
    for sgn in (1, -1):
        assy.add(pin(sgn * xl, PIN_LOW_Z), name=f"pin_low_{'r' if sgn>0 else 'l'}_{xl:.0f}", color=DARK)
        assy.add(pin(sgn * (xl + SHIFT), PIN_UP_Z), name=f"pin_up_{'r' if sgn>0 else 'l'}_{xl:.0f}", color=DARK)
for sgn in (1, -1):
    assy.add(pin(sgn * DRIVE_LOW_X, PIN_LOW_Z, length=40.0),
             name=f"pin_drive_{'r' if sgn>0 else 'l'}", color=DARK)
assy.add(pin(*PIVOT, d=6.0, length=44.0), name="pin_pivot", color=DARK)

if __name__ == "__main__":
    import os
    out = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(out, "plier_tool.step")
    try:
        assy.export(path)
    except AttributeError:
        assy.save(path)
    bb = assy.toCompound().BoundingBox()
    print("wrote", path)
    print(f"envelope with fixture: X {bb.xlen:.0f} x Y {bb.ylen:.0f} x Z {bb.zlen:.0f} mm")
    print(f"parallelogram arc drop over {SHIFT:.0f} mm travel: {ARC_DROP:.2f} mm")
    print(f"jaw swing angle: {SWING:.1f} deg (carrier stays parallel)")
