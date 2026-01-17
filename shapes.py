"""
Shape generator functions for creating procedural icons.
Each function generates SVG content for various fastener components.
Shapes are assumed to fit within a 100x100 viewbox unless otherwise specified.
"""

import math
from typing import Callable


class IconRegistry:
    top_generators: dict[str, Callable[..., str]] = {}
    side_generators: dict[str, Callable[..., str]] = {}


def icon_generator(which: str, names: list[str]):
    """Decorator to register icon generator functions."""
    match which:
        case "top":
            registry = IconRegistry.top_generators
        case "side":
            registry = IconRegistry.side_generators
        case _:
            raise ValueError(f"Unknown icon registry: {which}")

    def decorator(func: Callable[..., str]):
        for name in names:
            name_lower = name.lower()
            if name_lower in registry:
                raise ValueError(f"Icon generator for {name_lower} already registered in {which} registry")
            registry[name_lower] = func
        return func

    return decorator


## Generic shape components ##


def polygon_points(
    n: int,
    flat_to_flat: float,
    cx: float = 50,
    cy: float = 50,
    rotation_deg: float = 0,
) -> str:
    """Return a string of x,y points for an n-sided regular polygon sized by flat-to-flat distance.

    - flat_to_flat is the distance between opposite parallel sides (apothem*2).
    - cx, cy specify the center point of the polygon.
    - rotation_deg specifies the rotation of the polygon in degrees. Defaults to 0.
    """

    # circumradius R from flat-to-flat (2 * apothem = flat_to_flat), apothem = R * cos(pi/n)
    R = flat_to_flat / (2 * math.cos(math.pi / n))
    pts = []
    for i in range(n):
        angle_deg = rotation_deg + i * (360.0 / n)
        a = math.radians(angle_deg)
        x = cx + R * math.cos(a)
        y = cy + R * math.sin(a)
        pts.append(f"{x:.2f},{y:.2f}")
    return 'points="' + " ".join(pts) + '"'


def star(lobes: int, outer_radius: float, inner_radius: float) -> str:
    """Generate SVG path points for a star shape with given number of lobes and radii."""
    path = 'd="M '
    for i in range(lobes * 2):
        r = outer_radius if i % 2 == 0 else inner_radius
        angle_deg = i * (360.0 / (lobes * 2)) - 90  # start pointing up
        a = math.radians(angle_deg)
        x = 50 + r * math.cos(a)
        y = 50 + r * math.sin(a)
        path += f"{x:.2f} {y:.2f} "
        if i == 0:
            path += "L "
    path += ' Z"'
    return path


def annulus(outer_radius: float, inner_radius: float, color="#000000") -> str:
    """Generic annulus shape
    a ring with given outer and inner radii.
    """
    return f"""
    <circle cx="50" cy="50" r="{outer_radius}" fill="{color}" />
    <circle cx="50" cy="50" r="{inner_radius}" fill="#FFFFFF" />
    """


def cap_side(head_width: float, head_height: float) -> str:
    """Generic cap head side view
    a rounded rectangle, wider than it is tall
    """
    head = f"""
    <rect x="{(100 - head_width) / 2}" y="{100 - head_height - 80}" width="{head_width}" height="{head_height}" rx="{head_height/4}" ry="{head_height/4}" fill="#000000" />
    """
    return head


def button_side(head_diameter: float, head_height: float) -> str:
    """Generic button head side view
    a semi-ellipse on top of a rectangle.
    """
    head = f"""
    <ellipse cx="50" cy="{100 - head_height - 80 + head_height/2}" rx="{head_diameter/2}" ry="{head_height/2}" fill="#000000" />
    <rect x="{(100 - head_diameter) / 2}" y="{100 - head_height - 80 + head_height/2}" width="{head_diameter}" height="{head_height/2}" fill="#000000" />
    """
    return head


def countersunk_side(head_diameter: float = 50, head_height: float = 20) -> str:
    """Generic countersunk head side view
    a trapezoid centered in the field, smaller at the bottom.
    """
    head = f"""
    <path d="M {(100 - head_diameter) / 2} {100 - head_height - 80} L {(100 + head_diameter) / 2} {100 - head_height - 80} L {60} {100 - 80} L {40} {100 - 80} Z" fill="#000000" />
    """
    return head


def bolt_shaft(shaft_width: float, shaft_length: float, pointed=False) -> str:
    """Generic bolt shaft side view.
    A vertical rectangle (shaft) with diagonal lines to indicate threading.
    """
    origin_x = (100 - shaft_width) / 2
    origin_y = 100 - shaft_length
    chamfer_height = shaft_width / 4
    shaft_length = shaft_length - (shaft_width if pointed else chamfer_height)
    shaft = ""
    shaft += f'<rect x="{origin_x}" y="{origin_y}" width="{shaft_width}" height="{shaft_length}" fill="#000000" />'

    # Add threading lines
    num_threads = 6
    for i in range(num_threads):
        y = origin_y + (i + 1) * (shaft_length / (num_threads + 1))
        threads = f'<line x1="{origin_x}" y1="{y}" x2="{(100 + shaft_width) / 2}" y2="{y - shaft_width/4}" stroke="#FFFFFF" stroke-width="2"/>'
        shaft += threads

    # Add pointed tip if needed
    if pointed:
        # a triangle aligned with the bottom of the shaft rectangle, pointing downwards
        point = f'<path d="M {origin_x} {origin_y + shaft_length} L {50} {100} L {origin_x + shaft_width} {origin_y + shaft_length} Z" fill="#000000" />'
        shaft += point
    else:
        # a small chamfer at the bottom of the shaft
        # this should be a small trapezoid, with the top edge equal to shaft_width, and the bottom edge slightly smaller
        chamfer = f'<path d="M {origin_x} {origin_y + shaft_length} L {origin_x + shaft_width} {origin_y + shaft_length} L {origin_x + shaft_width - chamfer_height/2} {origin_y + shaft_length + chamfer_height} L {origin_x + chamfer_height/2} {origin_y + shaft_length + chamfer_height} Z" fill="#000000" />'
        shaft += chamfer

    return shaft


def nut_hex_top(flat_to_flat: float, color="#000000") -> str:
    """Hex nut, top view
    A hexagon with a circular hole in the center
    """
    # compute polygon points using helper
    points_str = polygon_points(6, flat_to_flat)
    hole_radius = flat_to_flat / 4
    return f"""
    <polygon {points_str} fill="{color}" />
    <circle cx="50" cy="50" r="{hole_radius}" fill="#FFFFFF" />
    """


def nut_hex_side(thickness: float, flat_to_flat: float, color="#000000") -> str:
    """Hex nut, side view
    A vertical rectangle with two horizontal lines representing the hex shape.
    """
    return f"""
    <rect x="{(100 - thickness) / 2}" y="{(100 - flat_to_flat) / 2}" width="{thickness}" height="{flat_to_flat}" fill="{color}" />
    <line x1="{(100 - thickness) / 2 - (flat_to_flat/4)}" y1="{(100 - flat_to_flat) / 2 + flat_to_flat * 0.25}" x2="{(100 + thickness) / 2 + (flat_to_flat/4)}" y2="{(100 - flat_to_flat) / 2 + flat_to_flat * 0.25}" stroke="#FFFFFF" stroke-width="2"/>
    <line x1="{(100 - thickness) / 2 - (flat_to_flat/4)}" y1="{(100 - flat_to_flat) / 2 + flat_to_flat * 0.75}" x2="{(100 + thickness) / 2 + (flat_to_flat/4)}" y2="{(100 - flat_to_flat) / 2 + flat_to_flat * 0.75}" stroke="#FFFFFF" stroke-width="2"/>
    """


## Screws ##


@icon_generator("side", names=["button_head", "button"])
def button_head_side() -> str:
    """Button head cap screw, side view.
    A vertical rectangle (shaft) with a flattened semi-circle on top, flat side down (head).
    """
    head_width = 50
    head_height = 20
    shaft_width = 25
    shaft_length = 80
    return f"""
    <svg width="100" height="100" viewBox="0 0 100 100">
        {button_side(head_width, head_height)}
        {bolt_shaft(shaft_width, shaft_length)}
    </svg>
    """


@icon_generator("side", names=["cap_head", "cap"])
def cap_head_side() -> str:
    """Socket head cap screw, side view.
    A vertical rectangle (shaft) with a rounded rectangle on top (head).
    """
    head_width = 50
    head_height = 30
    shaft_width = 25
    shaft_length = 80
    return f"""
    <svg width="100" height="100" viewBox="0 0 100 100">
        {cap_side(head_width, head_height)}
        {bolt_shaft(shaft_width, shaft_length)}
    </svg>
    """


@icon_generator("side", names=["hex_head", "hex", "bolt"])
def hex_head_side() -> str:
    """Hex head screw, side view.
    A vertical rectangle (shaft) with a hexagonal prism on top (head).
    """
    head_flat_to_flat = 50
    head_height = 30
    shaft_width = 25
    shaft_length = 80
    return f"""
    <svg width="100" height="100" viewBox="0 0 100 100">
        {cap_side(head_flat_to_flat, head_height)}
        {bolt_shaft(shaft_width, shaft_length)}
    </svg>
    """


@icon_generator("side", names=["flush_head", "flat_head", "flat", "countersunk"])
def flush_head_side() -> str:
    """Flat head screw, side view.
    A vertical rectangle (shaft) with a countersunk triangle on top (head).
    """
    head_diameter = 50
    shaft_width = 20
    shaft_length = 80
    return f"""
    <svg width="100" height="100" viewBox="0 0 100 100">
        {countersunk_side(head_diameter, shaft_width)}
        {bolt_shaft(shaft_width, shaft_length)}
    </svg>
    """


@icon_generator("side", names=["wood_screw", "wood"])
def wood_screw_side() -> str:
    """Wood screw, side view.
    A vertical rectangle (shaft) with a pointed tip and a countersunk head on top.
    """
    head_diameter = 50
    shaft_width = 20
    shaft_length = 80
    return f"""
    <svg width="100" height="100" viewBox="0 0 100 100">
        {countersunk_side(head_diameter, shaft_width)}
        {bolt_shaft(shaft_width, shaft_length, pointed=True)}
    </svg>
    """


## Washers ##


@icon_generator("side", names=["washer_std", "washer"])
def washer_std_side(outer_diameter: float = 80, inner_diameter: float = 35) -> str:
    """Flat washer, side view (vertical orientation).
    A thin rectangle with a hole in the center.
    """
    thickness = outer_diameter / 6
    return f"""
    <svg width="100" height="100" viewBox="0 0 100 100">
        <rect x="{(100 - thickness) / 2}" y="{(100 - outer_diameter) / 2}" width="{thickness}" height="{outer_diameter}" fill="#000000" />
        <rect x="{(100 - thickness) / 2}" y="{(100 - inner_diameter) / 2}" width="{thickness}" height="{inner_diameter}" fill="#FFFFFF" />
    </svg>
    """


@icon_generator("top", names=["washer_std", "washer"])
def washer_std_top(outer_diameter: float = 80, inner_diameter: float = 35) -> str:
    """Flat washer, top view.
    A ring (circle with a hole in the center).
    """
    return f"""
    <svg width="100" height="100" viewBox="0 0 100 100">
        {annulus(outer_diameter/2.0, inner_diameter/2.0)}
    </svg>
    """


@icon_generator("side", names=["washer_fender", "fender"])
def washer_fender_side(diameter: float = 80) -> str:
    """Fender washer, side view (vertical orientation).
    A thin rectangle with a small hole in the center.
    """
    return washer_std_side(diameter, diameter / 3.0)


@icon_generator("top", names=["washer_fender", "fender"])
def washer_fender_top(diameter: float = 80) -> str:
    """Fender washer, top view.
    A ring with large OD and small ID.
    """
    return washer_std_top(diameter, diameter / 3.0)


@icon_generator("side", names=["washer_split", "split"])
def washer_split_side(diameter: float = 80) -> str:
    """Split lock washer, side view.
    A thin helix-like shape, with a white line diagonally across the middle to indicate the split.
    """
    outer_diameter = diameter
    inner_diameter = diameter / 2
    thickness = diameter / 10
    return f"""
    <svg width="100" height="100" viewBox="0 0 100 100">
        <path d="M {(100-thickness)/2} {(100-outer_diameter)/2+5} Q {(100-thickness)/2-5} {50-5} {(100-thickness)/2} {50} Q {(100-thickness)/2+5} {50+5} {(100-thickness)/2} {(100+outer_diameter)/2-5}" stroke="#000000" stroke-width="{thickness}" fill="none"/>
        <line x2="{(100-thickness)/2 - 10}" y1="{(100-inner_diameter)/2}" x1="{(100+thickness)/2 + 10}" y2="{(100+inner_diameter)/2}" stroke="#FFFFFF" stroke-width="{thickness}"/>
    </svg>
    """


@icon_generator("top", names=["washer_split", "split"])
def washer_split_top(diameter: float = 80) -> str:
    """Split lock washer, top view.
    An annular ring with a gap on one side to indicate the split.
    """
    outer_radius = diameter / 2
    inner_radius = outer_radius / 2
    gap_angle = 20  # degrees
    gap_width = diameter / 10
    return f"""
    <svg width="100" height="100" viewBox="0 0 100 100">
        {annulus(outer_radius, inner_radius)}
        <rect x="{50}" y="{50-gap_width/2}" width="{50}" height="{gap_width}" transform="rotate({-gap_angle} 50 50)" fill="#FFFFFF" />
    </svg>
    """


@icon_generator("side", names=["washer_star_inner", "star_inner"])
def washer_star_inner_side(diameter: float = 80) -> str:
    """Internal star washer, side view.
    Similar to standard washer with teeth indication.
    """
    return washer_std_side(diameter, diameter / 2)


@icon_generator("top", names=["washer_star_inner", "star_inner"])
def washer_star_inner_top(diameter: float = 80) -> str:
    """Internal star washer, top view.
    A ring with internal teeth.
    """
    outer_radius = diameter * 0.5
    inner_radius = outer_radius * 0.5
    teeth = star(12, outer_radius * 0.8, inner_radius * 0.8)
    return f"""
    <svg width="100" height="100" viewBox="0 0 100 100">
        {annulus(outer_radius, inner_radius)}
        <path {teeth} fill="#FFFFFF"/>
        <circle cx="50" cy="50" r="{inner_radius*1.1}" fill="#FFFFFF"/>
    </svg>
    """


@icon_generator("side", names=["washer_star_outer", "star_outer", "star"])
def washer_star_outer_side(diameter: float = 80) -> str:
    """External star washer, side view.
    Similar to standard washer with outer teeth indication.
    """
    return washer_std_side(diameter, diameter / 2)


@icon_generator("top", names=["washer_star_outer", "star_outer", "star"])
def washer_star_outer_top(diameter: float = 80) -> str:
    """External star washer, top view.
    A ring with external teeth.
    """
    outer_radius = diameter * 0.4
    inner_radius = outer_radius * 0.7
    teeth = star(12, outer_radius * 1.3, inner_radius)
    return f"""
    <svg width="100" height="100" viewBox="0 0 100 100">
        <path {teeth} fill="#000000"/>
        <circle cx="50" cy="50" r="{outer_radius}" fill="#000000"/>
        <circle cx="50" cy="50" r="{inner_radius}" fill="#FFFFFF"/>
    </svg>
    """


## Nut generators ##


@icon_generator("top", names=["nut_standard", "nut"])
def nut_standard_top(diameter: float = 80) -> str:
    """Standard hex nut, top view"""
    return f"""
    <svg width="100" height="100" viewBox="0 0 100 100">
        {nut_hex_top(diameter)}
    </svg>
    """


@icon_generator("side", names=["nut_standard", "nut"])
def nut_standard_side(diameter: float = 80) -> str:
    """Standard hex nut, side view"""
    return f"""
    <svg width="100" height="100" viewBox="0 0 100 100">
        {nut_hex_side(30, diameter)}
    </svg>
    """


@icon_generator("top", names=["nut_thin", "thin_nut"])
def nut_thin_top(diameter: float = 80) -> str:
    """Thinner nut (smaller across-flats)"""
    return f"""
    <svg width="100" height="100" viewBox="0 0 100 100">
        {nut_hex_top(diameter)}
    </svg>
    """


@icon_generator("side", names=["nut_thin", "thin_nut"])
def nut_thin_side(diameter: float = 80) -> str:
    """Thinner nut (smaller across-flats) side view"""
    return f"""
    <svg width="100" height="100" viewBox="0 0 100 100">
        {nut_hex_side(30, diameter)}
    </svg>
    """


@icon_generator("top", names=["nut_lock", "nyloc"])
def nut_lock_top(diameter: float = 80) -> str:
    """Nyloc style: hex with a filled smaller ring (representing nylon insert)"""
    return f"""
    <svg width="100" height="100" viewBox="0 0 100 100">
        {nut_hex_top(diameter)}
        <circle cx="50" cy="50" r="{diameter * 0.2}" fill="#FFFFFF" />
    </svg>
    """


@icon_generator("side", names=["nut_lock", "nyloc"])
def nut_lock_side(diameter: float = 80) -> str:
    """Side view with a thin band on the top to indicate nylon insert"""
    thickness = 30
    radius = diameter * 0.5
    return f"""
    <svg width="100" height="100" viewBox="5 0 100 100">
        {nut_hex_side(thickness, diameter)}
        <rect x="{50}" y="{50-radius+diameter*0.1}" width="{thickness}" height="{diameter*0.8}" fill="#000000" />
    </svg>
    """


@icon_generator("top", names=["nut_flange", "flange_nut"])
def nut_flange_top(diameter: float = 80) -> str:
    """Flange nut:
    hex centered on a larger disk (simple rendering)
    Draw a dark flange disk with a black hexagon and central hole
    """
    return f"""
    <svg width="100" height="100" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="{diameter*0.6}" fill="#000000" />
        {nut_hex_top(diameter*0.9, color="#FFFFFF")}
        {nut_hex_top(diameter*0.8, color="#000000")}
    </svg>
    """


@icon_generator("side", names=["nut_flange", "flange_nut"])
def nut_flange_side(diameter: float = 80) -> str:
    """Side view with a flange plate at the base"""
    thickness = 30
    flange_diameter = diameter * 1.2
    flange_thickness = thickness * 0.4
    return f"""
    <svg width="100" height="100" viewBox="0 0 100 100">
        {nut_hex_side(thickness, diameter)}
        <rect x="{(100-thickness)/2}" y="{(100-flange_diameter)/2}" width="{flange_thickness}" height="{flange_diameter}" fill="#000000" />
    </svg>
    """


@icon_generator("top", names=["nut_cap", "cap_nut", "acorn", "acorn_nut"])
def nut_cap_top(diameter: float = 80) -> str:
    """Cap (acorn) nut
    circular dome on top of hex"""
    pts = polygon_points(6, diameter, rotation_deg=0)
    return f"""
    <svg width="100" height="100" viewBox="0 0 100 100">
        <polygon {pts} fill="#000000" />
        <circle cx="50" cy="50" r="{diameter * 0.4}" fill="#FFFFFF" />
        <circle cx="50" cy="50" r="{diameter * 0.35}" fill="#000000" />
    </svg>
    """


@icon_generator("side", names=["nut_cap", "cap_nut", "acorn", "acorn_nut"])
def nut_cap_side(diameter: float = 80) -> str:
    """Cap (acorn) nut side
    Dome on the side of hex profile"""
    thickness = 20
    return f"""
    <svg width="100" height="100" viewBox="0 0 100 100">
        <!--dome-->
        <ellipse cx="50" cy="50" rx="{diameter * 0.4}" ry="{diameter * 0.4}" fill="#000000" />
        <!--white rectangle to cut off the left side of the dome-->
        <rect x="0" y="0" height="100" width="50" fill="#FFFFFF" />

        <!--hex body-->
        <rect x="{(100) / 2 - thickness}" y="{(100 - diameter) / 2}" width="{thickness}" height="{diameter}" fill="#000000" />
        <rect x="{50}" y="{0}" width="{thickness*0.2}" height="{100}" fill="#FFFFFF" />
    </svg>
    """


@icon_generator("top", names=["nut_wing", "wing_nut", "wing"])
def nut_wing_top(diameter: float = 80) -> str:
    """Wing nut top
    Annular ring with a top and bottom rectangle representing the wings
    """
    wing_width = diameter * 0.25
    wing_height = diameter * 0.25
    wing_offset = 0
    return f"""
    <svg width="100" height="100" viewBox="0 0 100 100">
        {annulus(diameter*0.4, diameter*0.2)}
        <rect x="{(100 - wing_width) / 2}" y="{wing_offset}" width="{wing_width}" height="{wing_height}" transform="rotate(45 50 50)" fill="#000000" />
        <rect x="{(100 - wing_width) / 2}" y="{100 - wing_height - wing_offset}" width="{wing_width}" height="{wing_height}" transform="rotate(45 50 50)" fill="#000000" />
    </svg>
    """


@icon_generator("side", names=["nut_wing", "wing_nut", "wing"])
def nut_wing_side(diameter: float = 80) -> str:
    """wing nut side
    a vertical rectangle representing the base, with two polygons for the wings
    """
    wing_width = diameter * 0.6
    wing_height = diameter * 0.2
    inner_diameter = diameter * 0.6
    base_y = (100 - inner_diameter) / 2
    wing_angle = 60  # degrees

    return f"""
    <svg width="100" height="100" viewBox="5 0 100 100">
        <!-- Left wing -->
        <rect x="{50}" y="{base_y+wing_height}" width="{wing_width}" height="{wing_height}" transform="rotate({-wing_angle} {50} {50})" fill="#000000" />
        <!-- Right wing -->
        <rect x="{50}" y="{base_y+wing_height}" width="{wing_width}" height="{wing_height}" transform="rotate({wing_angle} {50} {50})" fill="#000000" />
        <!-- Base nut body -->
        {nut_hex_side(30, inner_diameter)}
    </svg>
    """


## Threaded insert generators ##


@icon_generator("top", names=["insert_heat", "heat_insert", "heat_set_insert", "hsi", "heat_set", "insert_press"])
def insert_heat_top(diameter: float = 80) -> str:
    """heat-set insert top - 20 pointed star, with a hole in the center"""
    points_str = star(20, diameter * 0.6, diameter * 0.5)
    return f"""
    <svg width="100" height="100" viewBox="0 0 100 100">
        <path {points_str} fill="#000000" />
        <circle cx="50" cy="50" r="{diameter * 0.2}" fill="#FFFFFF" />
    </svg>
    """


@icon_generator("side", names=["insert_heat", "heat_insert", "heat_set_insert", "hsi", "heat_set"])
def insert_heat_side(diameter: float = 80, length: float = 60) -> str:
    """heat-set insert side - stack of 4 rectangles with hatch lines to indicate knurling.
    1) full witdth, diagonal hatch, 1/3 overall height
    2) slightly narrower, no hatch, 1/6 overall height
    3) full width, diagonal hatch the opposite of 1, 1/3 overall height
    4) narrower, no hatch, 1/6 overall height

    The hatch lines are represented by white diagonal lines over the black base rectangles.
    The knurling angle is typically around 60 degrees.
    The knurl lines should be spaced evenly across the width of the wide insert sections (1 & 3).
    """

    wide_height = length / 3.0
    wide_width = diameter * 0.5
    narrow_height = length / 6.0
    narrow_width = diameter * 0.4
    top = max(100 - length * 1.3, 0)
    left = 5
    rects = [
        f'<rect x="{left + (100-wide_width)/2}"   y="{top}"               width="{wide_width}"   height="{wide_height}" fill="#000000" />',
        f'<rect x="{left + (100-narrow_width)/2}" y="{top + wide_height}" width="{narrow_width}" height="{narrow_height}" fill="#000000" />',
        f'<rect x="{left + (100-wide_width)/2}"   y="{top + wide_height + narrow_height}" width="{wide_width}" height="{wide_height}" fill="#000000" />',
        f'<rect x="{left + (100-narrow_width)/2}" y="{top + wide_height + narrow_height + wide_height}" width="{narrow_width}" height="{narrow_height}" fill="#000000" />',
    ]

    knurl_angle = 30  # degrees
    knurl_spacing = 10
    knurl_height = wide_height

    left_knurl_lines = ""
    right_knurl_lines = ""
    # Left slanting lines for top wide section
    for x in range(
        int((100 - wide_width) / 2),
        int((100 + wide_width) / 2) + knurl_spacing,
        knurl_spacing,
    ):
        x1 = x + left
        y1 = top
        x2 = x1 - knurl_height * math.tan(math.radians(knurl_angle))
        y2 = top + knurl_height
        left_knurl_lines += f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#FFFFFF" stroke-width="2"/>'
    # Right slanting lines for bottom wide section
    for x in range(
        int((100 - wide_width) / 2),
        int((100 + wide_width) / 2) + knurl_spacing,
        knurl_spacing,
    ):
        x1 = x + left
        y1 = top + wide_height + narrow_height
        x2 = x1 + knurl_height * math.tan(math.radians(knurl_angle))
        y2 = top + wide_height + narrow_height + knurl_height
        right_knurl_lines += f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#FFFFFF" stroke-width="2"/>'

    return f"""
    <svg width="100" height="100" viewBox="0 0 100 100">
        <!-- Base rectangles body -->
        {''.join(rects)}
        <!-- Hatch lines for knurling -->
        {left_knurl_lines}
        {right_knurl_lines}
    </svg>
    """


@icon_generator("top", names=["insert_wood", "wood_insert"])
def insert_wood_top(diameter: float = 80) -> str:
    """Wood insert:
    circle with radial serrations (teeth)
    """
    teeth = "".join(
        [
            f'<rect x="{50}" y="{50 + diameter*0.4}" width="{diameter*0.1}" height="{diameter*0.1}" transform="rotate({i*360/12} 50 50)" fill="#ffffff"/>'
            for i in range(12)
        ]
    )
    return f"""
    <svg width="100" height="100" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="{diameter * 0.5}" fill="#000000" />
        <circle cx="50" cy="50" r="{diameter * 0.2}" fill="#FFFFFF" />
        {teeth}
    </svg>
    """


@icon_generator("side", names=["insert_wood", "wood_insert"])
def insert_wood_side(diameter: float = 60) -> str:
    """Side view: vertical cylinder with diagonal notches representing serrations
    Each notch is a short diagonal line across the cylinder
    At the bottom of the cylinder, there should be a trapezoid to indicate the pointed tip
    """
    thread_spacing = 8
    radius = diameter / 2
    threads = "".join(
        [
            f'<line x1="{50-radius}" y1="{30 + i * thread_spacing}" x2="{50+radius}" y2="{30 + i * thread_spacing - radius * 0.4}" stroke="#FFFFFF" stroke-width="2"/>'
            for i in range(7)
        ]
    )
    return f"""
    <svg width="100" height="100" viewBox="0 0 100 100">
        <!--cylinder body-->
        <rect x="{50-radius}" y="{(100 - diameter * 0.7)/2}" width="{diameter}" height="{diameter * 0.7}" fill="#000000" />
        <!--tapered tip-->
        <path d="M {50-radius} {70} L {50+radius} {70} L {50+radius*0.7} {90} L {50-radius*0.7} {90} Z" fill="#000000" />
        <!--notches-->
        {threads}
        <rect x="{45}" y="{25}" width="{10}" height="{15}" fill="#FFFFFF" />
    </svg>
    """


@icon_generator("side", names=["insert_press", "press_insert"])
def insert_press_side(diameter: float = 60) -> str:
    """Side view - vertical cylinder narrowed body. The top and bottom have vertical white lines across them, indicating grooves."""
    radius = diameter / 2
    height = diameter * 1.2
    section_height = height * 0.25
    groove_spacing = diameter * 0.2
    num_grooves = 8
    upper_grooves = "".join(
        [
            f'<rect x="{50 - radius + i*groove_spacing - groove_spacing/3}" y="{100 - height - section_height}" width="{2}" height="{section_height}" fill="#FFFFFF"/>'
            for i in range(num_grooves)
        ]
    )
    lower_grooves = "".join(
        [
            f'<rect x="{50 - radius + i*groove_spacing - groove_spacing/2}" y="{(100 - height)/2 + height - section_height}" width="{2}" height="{section_height}" fill="#FFFFFF"/>'
            for i in range(num_grooves)
        ]
    )
    return f"""
    <svg width="100" height="100" viewBox="0 0 100 100">
        <!--upper section-->
        <rect x="{50 - radius}" y="{(100 - height)/2}" width="{diameter}" height="{section_height}" fill="#000000" />
        <!--lower section-->
        <rect x="{50 - radius}" y="{(100 - height)/2 + height - section_height}" width="{diameter}" height="{section_height}" fill="#000000" />
        <!--narrowed middle section-->
        <rect x="{50 - radius * 0.7}" y="{(100 - height)/2 + section_height}" width="{diameter * 0.7}" height="{height - 2 * section_height}" fill="#000000" />
        <!--grooves-->
        {upper_grooves}
        {lower_grooves}
    </svg>
    """


## Head top icons ##


@icon_generator("top", names=["head_hex", "hex_head", "hex"])
def head_hex_top(diameter: float = 80) -> str:
    """Hex head, top view
    A hexagon
    """
    flat_to_flat = diameter * math.sqrt(3) / 2
    points_str = polygon_points(6, flat_to_flat, rotation_deg=30)
    return f"""
    <svg width="100" height="100" viewBox="0 0 100 100">
        <polygon {points_str} fill="#000000" />
    </svg>
    """


@icon_generator("top", names=["head_socket", "socket_head", "socket"])
def head_socket_top(diameter: float = 80) -> str:
    """Socket Hex head, top view
    A circle with an inner hexagon
    """
    flat_to_flat = diameter / 2
    points_str = polygon_points(6, flat_to_flat)
    return f"""
    <svg width="100" height="100" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="{diameter * 0.5}" fill="#000000" />
        <polygon {points_str} fill="#FFFFFF" />
    </svg>
    """


@icon_generator("top", names=["head_torx", "torx_head", "torx"])
def head_torx_top(diameter: float = 80) -> str:
    """Torx head, top view
    A circle with a 6 lobed rounded star shape inside
    """
    lobes = 6
    path = star(lobes, diameter * 0.3, diameter * 0.2)
    return f"""
    <svg width="100" height="100" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="{diameter * 0.5}" fill="#000000" />
        <path {path} fill="#FFFFFF"/>
    </svg>
    """


@icon_generator("top", names=["head_square", "square_head", "square", "robertson", "robertson_head"])
def head_square_top(diameter: float = 80) -> str:
    """Square drive (aka Robertson) top
    A circle with a square in the center
    """
    square_size = diameter * 0.4
    return f"""
    <svg width="100" height="100" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="{diameter * 0.5}" fill="#000000" />
        <rect x="{50 - square_size/2}" y="{50 - square_size/2}" width="{square_size}" height="{square_size}" fill="#FFFFFF" />
    </svg>
    """


def slot(length: float = 75, width: float = 10, angle: float = 0) -> str:
    """Helper function to create a slot shape
    A rectangle centered in the viewbox
    """
    return f"""
    <rect x="{(100 - length) / 2}" y="{(100 - width) / 2}" width="{length}" height="{width}" transform="rotate({angle}, 50, 50)" fill="#FFFFFF" />
    """


@icon_generator("top", names=["head_slotted", "slotted_head", "slotted", "flat_head", "flat"])
def head_slotted_top(diameter: float = 80) -> str:
    """Slotted head, top view
    A circle with a horizontal bar through it
    """
    radius = diameter * 0.5
    return f"""
    <svg width="100" height="100" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="{radius}" fill="#000000" />
        {slot()}
    </svg>
    """


@icon_generator("top", names=["head_phillips", "phillips_head", "phillips"])
def head_phillips_top(diameter: float = 80) -> str:
    """Phillips head, top view
    A circle with a cross through it
    """
    radius = diameter * 0.5
    return f"""
    <svg width="100" height="100" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="{radius}" fill="#000000" />
        {slot()}
        {slot(angle = 90)}
    </svg>
    """


@icon_generator("top", names=["head_pozidriv", "pozidriv_head", "pozidriv", "pozi"])
def head_pozidriv_top(diameter: float = 80) -> str:
    """Pozidriv head, top view
    A circle with a cross and additional smaller bars at 45 degree angles
    """
    return f"""
    <svg width="100" height="100" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="{diameter * 0.5}" fill="#000000" />
        {slot(angle = 0)}
        {slot(angle = 90)}
        {slot(width = 5, length = 50, angle =45)}
        {slot(width = 5, length = 50, angle = -45)}
    </svg>
    """


## Bearings ##


@icon_generator("side", names=["bearing"])
def bearing_side(outer_diameter: float = 80, inner_diameter: float = 30) -> str:
    """Bearing, side view
    A circle with an inner ring representing the bearing
    """
    thickness = outer_diameter / 3
    return f"""
    <svg width="100" height="100" viewBox="0 0 100 100">
        <rect x="{(100 - thickness) / 2}" y="{(100 - outer_diameter) / 2}" width="{thickness}" height="{outer_diameter}" fill="#000000" />
        <rect x="{(100 - thickness) / 2}" y="{(100 - inner_diameter) / 2}" width="{thickness}" height="{inner_diameter}" fill="#FFFFFF" />
    </svg>
    """


@icon_generator("side", names=["bearing_flange", "flange_bearing"])
def bearing_flange_side(outer_diameter: float = 80, inner_diameter: float = 30) -> str:
    """Bearing with flange, side view
    A circle with an outer flange and an inner ring representing the bearing
    """
    thickness = outer_diameter / 3
    flange_diameter = outer_diameter * 1.2
    flange_height = (flange_diameter - outer_diameter) / 2
    return f"""
    <svg width="100" height="100" viewBox="0 0 100 100">
        <rect x="{(100 - thickness) / 2}" y="{(100 - outer_diameter) / 2}" width="{thickness}" height="{outer_diameter}" fill="#000000" />
        <rect x="{(100 - thickness) / 2}" y="{(100 - flange_diameter) / 2}" width="{flange_height}" height="{flange_diameter}" fill="#000000" />
        <rect x="{(100 - thickness) / 2}" y="{(100 - inner_diameter) / 2}" width="{thickness}" height="{inner_diameter}" fill="#FFFFFF" />
    </svg>
    """


@icon_generator("top", names=["bearing"])
def bearing_top(outer_diameter: float = 80, inner_diameter: float = 30) -> str:
    """Bearing, top view
    A circle with an inner ring representing the bearing
    """
    outer_radius = outer_diameter * 0.5
    inner_radius = inner_diameter * 0.5
    return f"""
    <svg width="100" height="100" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="{outer_radius}" fill="#000000" />
        <circle cx="50" cy="50" r="{outer_radius*0.8}" fill="#FFFFFF" />
        <circle cx="50" cy="50" r="{inner_radius*1.2}" fill="#000000" />
        <circle cx="50" cy="50" r="{inner_radius}" fill="#FFFFFF" />
    </svg>
    """


## Springs ##


@icon_generator("side", names=["spring", "coil", "coil_spring"])
def spring_side(diameter: float = 40, length: float = 60) -> str:
    """Spring, side view
    A vertical line, several diagonal lines representing the coils, and a final vertical line
    """
    start_y = (100 - length) / 2
    end_y = start_y + length
    start_x = (100 - diameter) / 2
    end_x = start_x + diameter
    num_coils = 7
    coil_spacing = diameter * 2 / (num_coils)

    lines = []
    for i in range(num_coils):
        y = start_y + i * coil_spacing
        if y + coil_spacing > end_y:
            if y < end_y:
                lines.append(
                    f'<line x1="{start_x}" y1="{y}" x2="{end_x}" y2="{end_y}" stroke="#000000" stroke-width="5" />'
                )
            break
        lines.append(
            f'<line x1="{start_x}" y1="{y}" x2="{end_x}" y2="{y + coil_spacing}" stroke="#000000" stroke-width="5" />'
        )
    return f"""
    <svg width="100" height="100" viewBox="0 0 100 100">
        <line x1="{start_x}" y1="{start_y}" x2="{end_x}" y2="{start_y}" stroke="#000000" stroke-width="8" />
        <line x1="{start_x}" y1="{end_y}" x2="{end_x}" y2="{end_y}" stroke="#000000" stroke-width="8" />
        {''.join(lines)}
    </svg>
    """


@icon_generator("top", names=["spring", "coil", "coil_spring"])
def spring_top(diameter: float = 80) -> str:
    """Spring, top view
    A slim annular ring
    """
    outer_radius = diameter * 0.5
    coil_radius = diameter * 0.35
    return f"""
    <svg width="100" height="100" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="{outer_radius}" fill="#000000" />
        <circle cx="50" cy="50" r="{coil_radius}" fill="#FFFFFF" />
    </svg>
    """
