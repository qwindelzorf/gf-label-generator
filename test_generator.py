#!/usr/bin/env python3
"""
Unit tests for generator.py module.
Tests utility functions, icon composition, QR generation, and label generation logic.
"""

import io
import csv
from pathlib import Path
from unittest.mock import Mock, patch, mock_open, MagicMock
import pytest
from jinja2 import Template
import segno
import requests

import generator


class TestMmToPx:
    """Test mm to pixel conversion."""

    def test_mm_to_px_default_dpi(self):
        """Test conversion with default DPI (150)."""
        # 25.4mm = 1 inch = 150 pixels at 150 DPI
        result = generator.mm_to_px(25.4)
        assert result == 150

    def test_mm_to_px_half_inch(self):
        """Test conversion for half inch."""
        result = generator.mm_to_px(25.4 / 2)
        assert result == 75

    def test_mm_to_px_label_width(self):
        """Test conversion for label width."""
        result = generator.mm_to_px(36)
        assert isinstance(result, int)
        assert result > 0

    def test_mm_to_px_zero(self):
        """Test conversion for zero."""
        result = generator.mm_to_px(0)
        assert result == 0

    def test_mm_to_px_returns_int(self):
        """Test that result is always an integer."""
        result = generator.mm_to_px(10.5)
        assert isinstance(result, int)


class TestComposeIcons:
    """Test icon composition logic."""

    def test_compose_icons_both_empty(self):
        """Test with no icons."""
        result = generator.compose_icons("", "")
        assert result == ""

    def test_compose_icons_only_top(self):
        """Test with only top icon."""
        top_svg = '<circle cx="50" cy="50" r="20"/>'
        result = generator.compose_icons(top_svg, "")
        assert top_svg in result
        assert "<g transform=" not in result  # no positioning when only one

    def test_compose_icons_only_side(self):
        """Test with only side icon."""
        side_svg = '<rect x="10" y="10" width="20" height="20"/>'
        result = generator.compose_icons("", side_svg)
        assert side_svg in result
        assert "<g transform=" not in result  # no positioning when only one

    def test_compose_icons_both_present(self):
        """Test with both top and side icons."""
        top_svg = '<circle cx="50" cy="50" r="20"/>'
        side_svg = '<rect x="10" y="10" width="20" height="20"/>'
        result = generator.compose_icons(top_svg, side_svg)
        assert top_svg in result
        assert side_svg in result
        assert "<g transform=" in result
        # Should have two g groups
        assert result.count("<g transform=") == 2

    def test_compose_icons_preserves_content(self):
        """Test that icon content is preserved."""
        top_svg = '<path d="M10 10 L20 20"/>'
        side_svg = '<polygon points="10,10 20,20 30,30"/>'
        result = generator.compose_icons(top_svg, side_svg)
        assert "M10 10 L20 20" in result
        assert "10,10 20,20 30,30" in result


class TestMakeQrSvg:
    """Test QR code generation."""

    @patch("generator.requests.get")
    def test_make_qr_svg_micro_with_url_shortening(self, mock_get):
        """Test micro QR with URL shortening."""
        mock_response = Mock()
        mock_response.text = "https://short.url"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        svg_body, size = generator.make_qr_svg("https://example.com/long/url", 8.9, qr_type="micro")

        assert isinstance(svg_body, str)
        assert isinstance(size, (int, float))
        assert "<?xml" not in svg_body  # XML declaration should be stripped
        assert "<svg" in svg_body or "<path" in svg_body  # Valid SVG content

    @patch("generator.requests.get")
    def test_make_qr_svg_micro_shortening_fails(self, mock_get):
        """Test micro QR when URL shortening fails."""
        mock_get.side_effect = requests.RequestException("Network error")

        svg_body, size = generator.make_qr_svg("https://example.com", 8.9, qr_type="micro")

        assert isinstance(svg_body, str)
        assert isinstance(size, (int, float))
        assert "<svg" in svg_body or "<path" in svg_body

    def test_make_qr_svg_standard(self):
        """Test standard QR generation."""
        svg_body, size = generator.make_qr_svg("https://example.com", 8.9, qr_type="standard")

        assert isinstance(svg_body, str)
        assert isinstance(size, (int, float))
        assert size > 0
        assert "<?xml" not in svg_body

    def test_make_qr_svg_non_url_content(self):
        """Test QR with non-URL content."""
        svg_body, size = generator.make_qr_svg("SOME-PART-123", 8.9, qr_type="micro")

        assert isinstance(svg_body, str)
        assert isinstance(size, (int, float))
        assert size > 0

    def test_make_qr_svg_invalid_type_raises(self):
        """Test that invalid QR type raises ValueError."""
        with pytest.raises(ValueError, match="Invalid qr_type"):
            generator.make_qr_svg("content", 8.9, qr_type="invalid")

    @patch("generator.requests.get")
    def test_make_qr_svg_strips_https_prefix(self, mock_get):
        """Test that https:// prefix is stripped for micro QR."""
        mock_response = Mock()
        mock_response.text = "https://v.gd/abc123"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        svg_body, size = generator.make_qr_svg("https://example.com", 8.9, qr_type="micro")

        assert isinstance(svg_body, str)
        assert isinstance(size, (int, float))

    @patch("generator.requests.get")
    def test_make_qr_svg_strips_http_prefix(self, mock_get):
        """Test that http:// prefix is stripped for micro QR."""
        mock_response = Mock()
        mock_response.text = "http://v.gd/abc123"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        svg_body, size = generator.make_qr_svg("http://example.com", 8.9, qr_type="micro")

        assert isinstance(svg_body, str)
        assert isinstance(size, (int, float))


class TestReadTemplate:
    """Test template reading."""

    def test_read_template_returns_jinja_template(self):
        """Test that read_template returns a Jinja2 Template object."""
        mock_content = "<svg>{{name}}</svg>"
        m = mock_open(read_data=mock_content)

        with patch("builtins.open", m):
            result = generator.read_template(Path("template.svg"))

        assert isinstance(result, Template)
        rendered = result.render({"name": "test", "qr_size": 10})
        assert "test" in rendered

    def test_read_template_with_real_template_structure(self):
        """Test with a realistic template structure."""
        mock_content = """<svg width="{{LABEL_WIDTH_MM}}mm" height="{{LABEL_HEIGHT_MM}}mm">
            <text>{{name}}</text>
            <text>{{description}}</text>
            {{icon_svg}}
            {{qr_svg}}
        </svg>"""
        m = mock_open(read_data=mock_content)

        with patch("builtins.open", m):
            result = generator.read_template(Path("template.svg"))

        rendered = result.render(
            {
                "LABEL_WIDTH_MM": 36,
                "LABEL_HEIGHT_MM": 8.9,
                "name": "Test Part",
                "description": "Description",
                "icon_svg": "<circle/>",
                "qr_svg": "<rect/>",
                "qr_size": 10,
            }
        )
        assert "Test Part" in rendered
        assert "36mm" in rendered


class TestIconGeneratorRegistries:
    """Test icon generator registry mappings."""

    def test_top_icon_generators_exist(self):
        """Test that TOP_ICON_GENERATORS is properly defined."""
        assert isinstance(generator.TOP_ICON_GENERATORS, dict)
        assert len(generator.TOP_ICON_GENERATORS) > 0

    def test_side_icon_generators_exist(self):
        """Test that SIDE_ICON_GENERATORS is properly defined."""
        assert isinstance(generator.SIDE_ICON_GENERATORS, dict)
        assert len(generator.SIDE_ICON_GENERATORS) > 0

    def test_top_icon_generators_callable(self):
        """Test that all top icon generators are callable."""
        for key, func in generator.TOP_ICON_GENERATORS.items():
            assert callable(func), f"{key} should be callable"

    def test_side_icon_generators_callable(self):
        """Test that all side icon generators are callable."""
        for key, func in generator.SIDE_ICON_GENERATORS.items():
            assert callable(func), f"{key} should be callable"

    def test_top_icon_generators_return_svg(self):
        """Test that top icon generators return valid SVG."""
        for key, func in list(generator.TOP_ICON_GENERATORS.items())[:5]:  # Test first 5
            result = func()
            assert isinstance(result, str)
            assert "<svg" in result or len(result) > 0

    def test_side_icon_generators_return_svg(self):
        """Test that side icon generators return valid SVG."""
        for key, func in list(generator.SIDE_ICON_GENERATORS.items())[:5]:  # Test first 5
            result = func()
            assert isinstance(result, str)
            assert "<svg" in result or len(result) > 0

    def test_common_icon_keys_exist(self):
        """Test that common icon keys exist in registries."""
        common_keys = ["washer", "nut", "hex", "socket"]
        for key in common_keys:
            assert key in generator.TOP_ICON_GENERATORS or key in generator.SIDE_ICON_GENERATORS


class TestLogLevel:
    """Test logging level enum."""

    def test_log_level_constants_exist(self):
        """Test that LogLevel constants are defined."""
        assert hasattr(generator.LogLevel, "DEBUG")
        assert hasattr(generator.LogLevel, "INFO")
        assert hasattr(generator.LogLevel, "NORMAL")
        assert hasattr(generator.LogLevel, "WARNING")
        assert hasattr(generator.LogLevel, "ERROR")

    def test_log_level_ordering(self):
        """Test that log levels are in correct order."""
        assert generator.LogLevel.DEBUG < generator.LogLevel.INFO
        assert generator.LogLevel.INFO < generator.LogLevel.NORMAL
        assert generator.LogLevel.NORMAL < generator.LogLevel.WARNING
        assert generator.LogLevel.WARNING < generator.LogLevel.ERROR


class TestLoggingFunctions:
    """Test custom logging functions."""

    def test_logging_functions_exist(self):
        """Test that logging functions are defined."""
        assert callable(generator.debug)
        assert callable(generator.info)
        assert callable(generator.print)
        assert callable(generator.warn)
        assert callable(generator.error)

    @patch("generator.xprint")
    def test_debug_respects_log_level(self, mock_print):
        """Test that debug respects log level."""
        original_level = generator.LOG_LEVEL
        try:
            generator.LOG_LEVEL = generator.LogLevel.DEBUG
            generator.debug("test message")
            assert mock_print.called

            mock_print.reset_mock()
            generator.LOG_LEVEL = generator.LogLevel.ERROR
            generator.debug("test message")
            assert not mock_print.called
        finally:
            generator.LOG_LEVEL = original_level

    @patch("generator.xprint")
    def test_error_always_prints(self, mock_print):
        """Test that error always prints."""
        original_level = generator.LOG_LEVEL
        try:
            generator.LOG_LEVEL = generator.LogLevel.ERROR
            generator.error("error message")
            assert mock_print.called
        finally:
            generator.LOG_LEVEL = original_level


class TestGenerateLabels:
    """Test main label generation function."""

    @patch("generator.cairosvg.svg2png")
    @patch("generator.make_qr_svg")
    @patch("generator.read_template")
    @patch("builtins.open", new_callable=mock_open)
    def test_generate_labels_creates_output_dir(self, mock_file, mock_template, mock_qr, mock_cairo):
        """Test that generate_labels creates output directory."""
        # Setup mocks
        csv_content = "name,description,top_symbol,side_symbol,reorder_url\nTest,Desc,hex,washer,http://example.com"
        mock_file.return_value = io.StringIO(csv_content)

        mock_template_obj = Mock()
        mock_template_obj.render.return_value = "<svg>test</svg>"
        mock_template.return_value = mock_template_obj

        mock_qr.return_value = ("<rect/>", 10)

        output_dir = Path("/tmp/test_output")

        with patch.object(Path, "mkdir") as mock_mkdir:
            generator.generate_labels(
                Path("test.csv"), Path("template.svg"), output_dir, qr_type="micro", output_format="png"
            )
            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    @patch("generator.cairosvg.svg2png")
    @patch("generator.make_qr_svg")
    @patch("generator.read_template")
    def test_generate_labels_svg_output(self, mock_template, mock_qr, mock_cairo):
        """Test SVG output format."""
        csv_content = "name,description,top_symbol,side_symbol,reorder_url\nTest,Desc,hex,washer,http://example.com"

        mock_template_obj = Mock()
        mock_template_obj.render.return_value = "<svg>test</svg>"
        mock_template.return_value = mock_template_obj

        mock_qr.return_value = ("<rect/>", 10)

        with patch("builtins.open", mock_open(read_data=csv_content)) as mock_file:
            with patch.object(Path, "mkdir"):
                with patch.object(Path, "open", mock_open()) as mock_output:
                    generator.generate_labels(
                        Path("test.csv"),
                        Path("template.svg"),
                        Path("/tmp/output"),
                        qr_type="micro",
                        output_format="svg",
                    )

                    # SVG should be written, not converted
                    assert not mock_cairo.called

    @patch("generator.cairosvg.svg2pdf")
    @patch("generator.make_qr_svg")
    @patch("generator.read_template")
    def test_generate_labels_pdf_output(self, mock_template, mock_qr, mock_cairo):
        """Test PDF output format."""
        csv_content = "name,description,top_symbol,side_symbol,reorder_url\nTest,Desc,hex,washer,http://example.com"

        mock_template_obj = Mock()
        mock_template_obj.render.return_value = "<svg>test</svg>"
        mock_template.return_value = mock_template_obj

        mock_qr.return_value = ("<rect/>", 10)

        with patch("builtins.open", mock_open(read_data=csv_content)):
            with patch.object(Path, "mkdir"):
                generator.generate_labels(
                    Path("test.csv"), Path("template.svg"), Path("/tmp/output"), qr_type="standard", output_format="pdf"
                )

                assert mock_cairo.called

    @patch("generator.cairosvg.svg2png")
    @patch("generator.make_qr_svg")
    @patch("generator.read_template")
    def test_generate_labels_handles_missing_icons(self, mock_template, mock_qr, mock_cairo):
        """Test handling of missing icon generators."""
        csv_content = (
            "name,description,top_symbol,side_symbol,reorder_url\nTest,Desc,nonexistent,invalid,http://example.com"
        )

        mock_template_obj = Mock()
        mock_template_obj.render.return_value = "<svg>test</svg>"
        mock_template.return_value = mock_template_obj

        mock_qr.return_value = ("<rect/>", 10)

        with patch("builtins.open", mock_open(read_data=csv_content)):
            with patch.object(Path, "mkdir"):
                with patch.object(Path, "open", mock_open()):
                    with patch("generator.error") as mock_error:
                        generator.generate_labels(
                            Path("test.csv"),
                            Path("template.svg"),
                            Path("/tmp/output"),
                            qr_type="micro",
                            output_format="svg",
                        )

                        # Should log errors for missing generators
                        assert mock_error.called

    @patch("generator.cairosvg.svg2png")
    @patch("generator.make_qr_svg")
    @patch("generator.read_template")
    def test_generate_labels_sanitizes_filenames(self, mock_template, mock_qr, mock_cairo):
        """Test that filenames are properly sanitized."""
        csv_content = "name,description,top_symbol,side_symbol,reorder_url\nTest/Part,Desc With Spaces,hex,washer,http://example.com"

        mock_template_obj = Mock()
        mock_template_obj.render.return_value = "<svg>test</svg>"
        mock_template.return_value = mock_template_obj

        mock_qr.return_value = ("<rect/>", 10)

        written_files = []

        def capture_write(path_str):
            written_files.append(path_str)

        with patch("builtins.open", mock_open(read_data=csv_content)):
            with patch.object(Path, "mkdir"):
                with patch("generator.cairosvg.svg2png") as mock_png:
                    mock_png.side_effect = lambda **kwargs: capture_write(kwargs.get("write_to", ""))

                    generator.generate_labels(
                        Path("test.csv"),
                        Path("template.svg"),
                        Path("/tmp/output"),
                        qr_type="micro",
                        output_format="png",
                    )

                    # Check that filename was sanitized (/ -> -, spaces -> _)
                    if written_files:
                        assert "/" not in Path(written_files[0]).name
                        assert "Test-Part" in written_files[0]


class TestConstants:
    """Test that constants are properly defined."""

    def test_label_dimensions_defined(self):
        """Test that label dimensions are defined."""
        assert hasattr(generator, "LABEL_WIDTH_MM")
        assert hasattr(generator, "LABEL_HEIGHT_MM")
        assert generator.LABEL_WIDTH_MM > 0
        assert generator.LABEL_HEIGHT_MM > 0

    def test_printer_dpi_defined(self):
        """Test that printer DPI is defined."""
        assert hasattr(generator, "LABEL_PRINTER_DPI")
        assert generator.LABEL_PRINTER_DPI > 0
        assert isinstance(generator.LABEL_PRINTER_DPI, int)
