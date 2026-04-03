#!/usr/bin/env python3
"""
Increases saturation of a .tdesktop-palette file.
Usage: saturate_palette.py <palette_file> [saturation_factor]
  saturation_factor: multiplier applied to HSL saturation (default: 1.8)
  Examples: 1.5 = subtle, 1.8 = noticeable, 2.5 = vivid
"""

import sys
import colorsys
import re
from pathlib import Path


def hex_to_rgb(hex_color: str) -> tuple[float, float, float]:
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return r / 255.0, g / 255.0, b / 255.0


def rgb_to_hex(r: float, g: float, b: float) -> str:
    return "#{:02x}{:02x}{:02x}".format(
        round(r * 255), round(g * 255), round(b * 255)
    )


def saturate(hex_color: str, factor: float) -> str:
    r, g, b = hex_to_rgb(hex_color)
    h, l, s = colorsys.rgb_to_hls(r, g, b)

    # Skip near-black and near-white — saturating them produces artifacts
    if l < 0.02 or l > 0.97:
        return hex_color

    s = min(1.0, s * factor)
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return rgb_to_hex(r, g, b)


def process_palette(path: Path, factor: float) -> None:
    lines = path.read_text().splitlines()
    result = []

    for line in lines:
        # Match lines like: keyName: #rrggbb
        match = re.match(r"^(\w+:\s*)(#[0-9a-fA-F]{6})\s*$", line)
        if match:
            prefix, color = match.group(1), match.group(2)
            result.append(f"{prefix}{saturate(color, factor)}")
        else:
            result.append(line)

    path.write_text("\n".join(result) + "\n")


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <palette_file> [saturation_factor]")
        sys.exit(1)

    palette_path = Path(sys.argv[1])
    if not palette_path.exists():
        print(f"Error: {palette_path} not found")
        sys.exit(1)

    factor = float(sys.argv[2]) if len(sys.argv) > 2 else 1.8

    process_palette(palette_path, factor)
    print(f"Saturated {palette_path} (factor: {factor})")


if __name__ == "__main__":
    main()
