from pathlib import Path
import shapes


def test_generate_all_icon_svgs():
    """Generate all top/side icon SVGs and write them to output folders.

    Creates `output/shapes/top` and `output/shapes/side` and writes one SVG
    file per registered icon generator. Asserts that each generator returns
    a non-empty SVG string.
    """
    base_out = Path("output") / "shapes"
    top_dir = base_out / "top"
    side_dir = base_out / "side"
    top_dir.mkdir(parents=True, exist_ok=True)
    side_dir.mkdir(parents=True, exist_ok=True)

    # Top view generators
    for name, fn in shapes.IconRegistry.top_generators.items():
        svg = fn()
        assert isinstance(svg, str) and svg.strip(), f"Top icon '{name}' returned empty"
        # Basic sanity check that the output contains SVG markup
        assert "<svg" in svg or "<polygon" in svg or "<circle" in svg
        (top_dir / f"{name}.svg").write_text(svg, encoding="utf-8")

    # Side view generators
    for name, fn in shapes.IconRegistry.side_generators.items():
        svg = fn()
        assert isinstance(svg, str) and svg.strip(), f"Side icon '{name}' returned empty"
        assert "<svg" in svg or "<rect" in svg or "<path" in svg
        (side_dir / f"{name}.svg").write_text(svg, encoding="utf-8")
