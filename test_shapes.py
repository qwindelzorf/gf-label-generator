#!/usr/bin/env python3
"""
Unit tests for shapes.py module.
Tests shape generator functions and helper utilities.
"""

import math
import pytest
import shapes


class TestHelperFunctions:
    """Test generic shape helper functions."""

    def test_polygon_points_hexagon(self):
        """Test hexagon points generation."""
        result = shapes.polygon_points(6, 50)
        assert 'points="' in result
        assert result.endswith('"')
        # Should have 6 coordinate pairs
        coords = result.split('"')[1].split()
        assert len(coords) == 6

    def test_polygon_points_square(self):
        """Test square points generation."""
        result = shapes.polygon_points(4, 40, cx=50, cy=50)
        assert 'points="' in result
        coords = result.split('"')[1].split()
        assert len(coords) == 4

    def test_polygon_points_custom_center(self):
        """Test polygon with custom center."""
        result = shapes.polygon_points(3, 30, cx=25, cy=75)
        assert 'points="' in result
        # Verify it's a valid SVG points attribute
        coords = result.split('"')[1].split()
        assert len(coords) == 3

    def test_polygon_points_custom_rotation(self):
        """Test polygon with custom rotation."""
        result = shapes.polygon_points(6, 50, rotation_deg=45)
        assert 'points="' in result
        coords = result.split('"')[1].split()
        assert len(coords) == 6

    def test_star_generates_path(self):
        """Test star path generation."""
        result = shapes.star(5, 30, 15)
        assert 'd="M ' in result
        assert ' Z"' in result
        assert "L " in result

    def test_star_different_lobes(self):
        """Test star with different lobe counts."""
        result_5 = shapes.star(5, 30, 15)
        result_12 = shapes.star(12, 30, 15)
        assert result_5 != result_12
        # 12-lobe star should have more coordinate pairs
        assert len(result_12) > len(result_5)

    def test_annulus_creates_circles(self):
        """Test annulus (ring) generation."""
        result = shapes.annulus(40, 20)
        assert result.count("<circle") == 2
        assert 'r="40"' in result
        assert 'r="20"' in result
        assert 'fill="#000000"' in result
        assert 'fill="#FFFFFF"' in result

    def test_cap_side_generates_rect(self):
        """Test cap head side view generation."""
        result = shapes.cap_side(50, 30)
        assert "<rect" in result
        assert 'fill="#000000"' in result
        assert "rx=" in result  # rounded corners
        assert "ry=" in result

    def test_button_side_generates_ellipse_and_rect(self):
        """Test button head side view generation."""
        result = shapes.button_side(50, 20)
        assert "<ellipse" in result
        assert "<rect" in result
        assert 'fill="#000000"' in result

    def test_countersunk_side_generates_path(self):
        """Test countersunk head side view generation."""
        result = shapes.countersunk_side(50, 20)
        assert "<path" in result
        assert 'd="M' in result
        assert 'fill="#000000"' in result

    def test_bolt_shaft_generates_rect_and_threads(self):
        """Test bolt shaft generation with threading."""
        result = shapes.bolt_shaft(25, 80)
        assert "<rect" in result
        assert "<line" in result  # threading lines
        assert 'stroke="#FFFFFF"' in result

    def test_bolt_shaft_pointed(self):
        """Test bolt shaft with pointed tip."""
        result = shapes.bolt_shaft(25, 80, pointed=True)
        assert "<rect" in result
        assert "<path" in result  # pointed tip
        assert "<line" in result  # threading

    def test_nut_hex_top_generates_polygon_and_circle(self):
        """Test hex nut top view."""
        result = shapes.nut_hex_top(50)
        assert "<polygon" in result
        assert "<circle" in result
        assert 'fill="#000000"' in result
        assert 'fill="#FFFFFF"' in result

    def test_nut_hex_side_generates_rect_and_lines(self):
        """Test hex nut side view."""
        result = shapes.nut_hex_side(30, 50)
        assert "<rect" in result
        assert "<line" in result
        assert result.count("<line") == 2  # two horizontal lines


class TestScrewGenerators:
    """Test screw-related shape generators."""

    def test_button_head_side(self):
        """Test button head screw side view."""
        result = shapes.button_head_side()
        assert "<svg" in result
        assert 'viewBox="0 0 100 100"' in result
        assert "<ellipse" in result
        assert "<rect" in result

    def test_cap_head_side(self):
        """Test socket head cap screw side view."""
        result = shapes.cap_head_side()
        assert "<svg" in result
        assert 'viewBox="0 0 100 100"' in result
        assert "<rect" in result

    def test_hex_head_side(self):
        """Test hex head screw side view."""
        result = shapes.hex_head_side()
        assert "<svg" in result
        assert 'viewBox="0 0 100 100"' in result
        assert "<rect" in result

    def test_flat_head_side(self):
        """Test flat head screw side view."""
        result = shapes.flat_head_side()
        assert "<svg" in result
        assert "<path" in result  # countersunk head

    def test_wood_screw_side(self):
        """Test wood screw side view."""
        result = shapes.wood_screw_side()
        assert "<svg" in result
        assert "<path" in result  # pointed tip


class TestWasherGenerators:
    """Test washer-related shape generators."""

    def test_washer_std_top(self):
        """Test standard washer top view."""
        result = shapes.washer_std_top()
        assert "<svg" in result
        assert "<circle" in result
        assert result.count("<circle") == 2  # outer and inner

    def test_washer_std_side(self):
        """Test standard washer side view."""
        result = shapes.washer_std_side()
        assert "<svg" in result
        assert "<rect" in result
        assert result.count("<rect") == 2  # outer and inner

    def test_washer_std_top_custom_diameter(self):
        """Test washer with custom diameter."""
        result = shapes.washer_std_top(outer_diameter=60, inner_diameter=20)
        assert "<svg" in result
        assert "<circle" in result

    def test_washer_fender_top(self):
        """Test fender washer top view."""
        result = shapes.washer_fender_top()
        assert "<svg" in result
        assert "<circle" in result

    def test_washer_fender_side(self):
        """Test fender washer side view."""
        result = shapes.washer_fender_side()
        assert "<svg" in result
        assert "<rect" in result

    def test_washer_split_top(self):
        """Test split lock washer top view."""
        result = shapes.washer_split_top()
        assert "<svg" in result
        assert "<circle" in result
        assert "<rect" in result  # gap indicator

    def test_washer_split_side(self):
        """Test split lock washer side view."""
        result = shapes.washer_split_side()
        assert "<svg" in result
        assert "<path" in result  # helix
        assert "<line" in result  # split indicator

    def test_washer_star_inner_top(self):
        """Test internal star washer top view."""
        result = shapes.washer_star_inner_top()
        assert "<svg" in result
        assert "<circle" in result
        assert "<path" in result  # star teeth

    def test_washer_star_inner_side(self):
        """Test internal star washer side view."""
        result = shapes.washer_star_inner_side()
        assert "<svg" in result
        assert "<rect" in result

    def test_washer_star_outer_top(self):
        """Test external star washer top view."""
        result = shapes.washer_star_outer_top()
        assert "<svg" in result
        assert "<path" in result  # star teeth

    def test_washer_star_outer_side(self):
        """Test external star washer side view."""
        result = shapes.washer_star_outer_side()
        assert "<svg" in result
        assert "<rect" in result


class TestNutGenerators:
    """Test nut-related shape generators."""

    def test_nut_standard_top(self):
        """Test standard nut top view."""
        result = shapes.nut_standard_top()
        assert "<svg" in result
        assert "<polygon" in result
        assert "<circle" in result

    def test_nut_standard_side(self):
        """Test standard nut side view."""
        result = shapes.nut_standard_side()
        assert "<svg" in result
        assert "<rect" in result
        assert "<line" in result

    def test_nut_thin_top(self):
        """Test thin nut top view."""
        result = shapes.nut_thin_top()
        assert "<svg" in result
        assert "<polygon" in result

    def test_nut_thin_side(self):
        """Test thin nut side view."""
        result = shapes.nut_thin_side()
        assert "<svg" in result
        assert "<rect" in result

    def test_nut_lock_top(self):
        """Test lock nut (nyloc) top view."""
        result = shapes.nut_lock_top()
        assert "<svg" in result
        assert "<polygon" in result
        assert result.count("<circle") == 2  # hole and nylon insert

    def test_nut_lock_side(self):
        """Test lock nut side view."""
        result = shapes.nut_lock_side()
        assert "<svg" in result
        assert "<rect" in result

    def test_nut_flange_top(self):
        """Test flange nut top view."""
        result = shapes.nut_flange_top()
        assert "<svg" in result
        assert "<circle" in result
        assert "<polygon" in result

    def test_nut_flange_side(self):
        """Test flange nut side view."""
        result = shapes.nut_flange_side()
        assert "<svg" in result
        assert "<rect" in result

    def test_nut_cap_top(self):
        """Test cap (acorn) nut top view."""
        result = shapes.nut_cap_top()
        assert "<svg" in result
        assert "<polygon" in result
        assert "<circle" in result

    def test_nut_cap_side(self):
        """Test cap nut side view."""
        result = shapes.nut_cap_side()
        assert "<svg" in result
        assert "<ellipse" in result  # dome
        assert "<rect" in result

    def test_nut_wing_top(self):
        """Test wing nut top view."""
        result = shapes.nut_wing_top()
        assert "<svg" in result
        assert "<circle" in result
        assert "<rect" in result  # wings

    def test_nut_wing_side(self):
        """Test wing nut side view."""
        result = shapes.nut_wing_side()
        assert "<svg" in result
        assert "<rect" in result


class TestInsertGenerators:
    """Test threaded insert generators."""

    def test_insert_heat_top(self):
        """Test heat-set insert top view."""
        result = shapes.insert_heat_top()
        assert "<svg" in result
        assert "<path" in result  # star pattern
        assert "<circle" in result  # center hole

    def test_insert_heat_side(self):
        """Test heat-set insert side view."""
        result = shapes.insert_heat_side()
        assert "<svg" in result
        assert "<rect" in result  # body sections
        assert "<line" in result  # knurling lines

    def test_insert_wood_top(self):
        """Test wood insert top view."""
        result = shapes.insert_wood_top()
        assert "<svg" in result
        assert "<circle" in result
        assert "<path" in result  # teeth

    def test_insert_wood_side(self):
        """Test wood insert side view."""
        result = shapes.insert_wood_side()
        assert "<svg" in result
        assert "<rect" in result

    def test_insert_press_top(self):
        """Test press-fit insert top view."""
        result = shapes.insert_press_top()
        assert "<svg" in result
        assert "<circle" in result

    def test_insert_press_side(self):
        """Test press-fit insert side view."""
        result = shapes.insert_press_side()
        assert "<svg" in result
        assert "<rect" in result


class TestHeadGenerators:
    """Test screw head top view generators."""

    def test_head_hex_top(self):
        """Test hex head top view."""
        result = shapes.head_hex_top()
        assert "<svg" in result
        assert "<polygon" in result

    def test_head_socket_top(self):
        """Test socket head top view."""
        result = shapes.head_socket_top()
        assert "<svg" in result
        assert "<circle" in result
        assert "<polygon" in result  # inner hex

    def test_head_torx_top(self):
        """Test Torx head top view."""
        result = shapes.head_torx_top()
        assert "<svg" in result
        assert "<circle" in result
        assert "<path" in result  # star pattern

    def test_head_slotted_top(self):
        """Test slotted head top view."""
        result = shapes.head_slotted_top()
        assert "<svg" in result
        assert "<circle" in result
        assert "<rect" in result  # slot

    def test_head_phillips_top(self):
        """Test Phillips head top view."""
        result = shapes.head_phillips_top()
        assert "<svg" in result
        assert "<circle" in result
        assert result.count("<rect") == 2  # cross

    def test_head_square_top(self):
        """Test square drive (Robertson) head top view."""
        result = shapes.head_square_top()
        assert "<svg" in result
        assert "<circle" in result
        assert "<rect" in result  # square drive

    def test_head_pozidriv_top(self):
        """Test Pozidriv head top view."""
        result = shapes.head_pozidriv_top()
        assert "<svg" in result
        assert "<circle" in result
        assert result.count("<rect") == 4  # cross plus angled bars


class TestSVGValidity:
    """Test that generated SVGs are valid and well-formed."""

    def test_all_generators_return_svg(self):
        """Test that all generator functions return valid SVG strings."""
        generators = [
            shapes.button_head_side,
            shapes.cap_head_side,
            shapes.hex_head_side,
            shapes.flat_head_side,
            shapes.wood_screw_side,
            shapes.washer_std_top,
            shapes.washer_std_side,
            shapes.washer_fender_top,
            shapes.washer_fender_side,
            shapes.washer_split_top,
            shapes.washer_split_side,
            shapes.washer_star_inner_top,
            shapes.washer_star_inner_side,
            shapes.washer_star_outer_top,
            shapes.washer_star_outer_side,
            shapes.nut_standard_top,
            shapes.nut_standard_side,
            shapes.nut_thin_top,
            shapes.nut_thin_side,
            shapes.nut_lock_top,
            shapes.nut_lock_side,
            shapes.nut_flange_top,
            shapes.nut_flange_side,
            shapes.nut_cap_top,
            shapes.nut_cap_side,
            shapes.nut_wing_top,
            shapes.nut_wing_side,
            shapes.insert_heat_top,
            shapes.insert_heat_side,
            shapes.insert_wood_top,
            shapes.insert_wood_side,
            shapes.insert_press_top,
            shapes.insert_press_side,
            shapes.head_hex_top,
            shapes.head_socket_top,
            shapes.head_torx_top,
            shapes.head_slotted_top,
            shapes.head_phillips_top,
            shapes.head_square_top,
            shapes.head_pozidriv_top,
        ]

        for gen in generators:
            result = gen()
            assert isinstance(result, str)
            assert "<svg" in result
            assert "</svg>" in result
            # Should contain viewBox
            assert "viewBox=" in result
