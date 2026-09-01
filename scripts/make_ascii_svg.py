#!/usr/bin/env python3
"""
scripts/make_ascii_svg.py
Generates the animated ASCII portrait SVG (avi-ascii.svg).
- Resamples source-prepped.png into a ~96x56 character grid
- Density ramp: RAMP = " .:-=+*cs#%@"
- Monochromatic light gray on dark terminal (#0d1117)
- Perfectly centered horizontally and vertically within the terminal window
- Staggered typing reveal animation (SMIL + CSS keyframes)
- Matches exact rendered height of info-card (480px) for symmetry
"""

import sys
import os
import html
from pathlib import Path
import numpy as np
from PIL import Image

RAMP = " .:-=+*cs#%@"


def generate_ascii_art(image_path: str, cols: int = 96, rows: int = 56):
    img = Image.open(image_path)
    
    # Accurate bounding box detection and centering
    arr_full = np.array(img)
    non_white = np.where(arr_full < 250)
    if len(non_white[0]) > 0:
        min_y = max(0, int(non_white[0].min()) - 20)
        max_y = int(non_white[0].max())
        min_x = int(non_white[1].min())
        max_x = int(non_white[1].max())
        
        # Crop precisely around content
        img_cropped = img.crop((min_x, min_y, max_x, max_y))
    else:
        img_cropped = img

    # High quality LANCZOS resampling
    small = img_cropped.resize((cols, rows), Image.Resampling.LANCZOS)
    arr = np.array(small)
    ramp_len = len(RAMP)

    lines = []
    for r in range(rows):
        line_chars = []
        for c in range(cols):
            val = int(arr[r, c])
            idx = int((255 - val) / 255.0 * (ramp_len - 1))
            idx = max(0, min(ramp_len - 1, idx))
            line_chars.append(RAMP[idx])
        lines.append("".join(line_chars))

    return lines


def create_ascii_svg(lines: list, output_path: str = "avi-ascii.svg"):
    rows = len(lines)
    cols = len(lines[0])

    # Monospace character dimensions
    char_w = 5.5
    line_h = 11.2

    content_w = cols * char_w
    content_h = rows * line_h

    svg_w = 573
    target_rendered_h = 480
    display_w = 370
    svg_h = int(target_rendered_h * svg_w / display_w)  # 743px

    # Calculate exact horizontal and vertical centering
    pad_x = (svg_w - content_w) / 2
    header_h = 30
    avail_h = svg_h - header_h
    pad_top = header_h + int((avail_h - content_h) / 2) + 2

    stagger = 0.035
    duration = 0.20

    css_rules = []
    clips = []
    text_elements = []

    css_rules.append(f"""
      @keyframes revealWidth {{
        0% {{ width: 0px; }}
        100% {{ width: {int(content_w + 10)}px; }}
      }}
      .term-bg {{ fill: #0d1117; stroke: #30363d; stroke-width: 1.5; rx: 10px; }}
      .term-header {{ fill: #161b22; }}
      .term-title {{ fill: #8b949e; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 11px; font-weight: 500; }}
      .ascii-text {{
        fill: #c9d1d9;
        font-family: 'Consolas', 'Cascadia Code', 'Fira Code', 'Courier New', monospace;
        font-size: 8.8px;
        letter-spacing: 0px;
        white-space: pre;
      }}
    """)

    for i, line in enumerate(lines):
        clip_id = f"cp-{i}"
        y_pos = pad_top + i * line_h
        begin_sec = 0.10 + i * stagger

        css_rules.append(f"""
      .clip-rect-{i} {{
        width: 0px;
        animation: revealWidth {duration}s cubic-bezier(0.2, 0.0, 0.38, 0.9) {begin_sec:.3f}s forwards;
      }}""")

        clip_svg = f"""    <clipPath id="{clip_id}">
      <rect class="clip-rect-{i}" x="{pad_x - 2:.1f}" y="{y_pos - 9:.1f}" width="0" height="{line_h + 2}">
        <animate attributeName="width" from="0" to="{int(content_w + 10)}" dur="{duration}s" begin="{begin_sec:.3f}s" fill="freeze" />
      </rect>
    </clipPath>"""
        clips.append(clip_svg)

        escaped_line = html.escape(line)
        text_el = f"""    <g clip-path="url(#{clip_id})">
      <text x="{pad_x:.1f}" y="{y_pos:.1f}" class="ascii-text" xml:space="preserve">{escaped_line}</text>
    </g>"""
        text_elements.append(text_el)

    clips_str = "\n".join(clips)
    texts_str = "\n".join(text_elements)
    css_str = "\n".join(css_rules)

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">
  <defs>
    <style>
{css_str}
    </style>
{clips_str}
  </defs>

  <!-- Terminal Window Background -->
  <rect x="1" y="1" width="{svg_w - 2}" height="{svg_h - 2}" class="term-bg" />

  <!-- Terminal Header Bar -->
  <path d="M 1,11 A 10,10 0 0,1 11,1 L {svg_w - 11},1 A 10,10 0 0,1 {svg_w - 1},11 L {svg_w - 1},30 L 1,30 Z" class="term-header" />
  <line x1="1" y1="30" x2="{svg_w - 1}" y2="30" stroke="#30363d" stroke-width="1" />

  <!-- Terminal Window Buttons -->
  <circle cx="18" cy="15" r="4.5" fill="#ff5f56" />
  <circle cx="32" cy="15" r="4.5" fill="#ffbd2e" />
  <circle cx="46" cy="15" r="4.5" fill="#27c93f" />

  <!-- Header Title -->
  <text x="{svg_w // 2}" y="19" text-anchor="middle" class="term-title">julianotx@terminal ~ portrait.ascii</text>

  <!-- Centered ASCII Lines with typing animation -->
{texts_str}
</svg>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)

    print(f"[+] ASCII SVG generated and centered successfully: {output_path} ({svg_w}x{svg_h})")


def main():
    img_path = "source-prepped.png"
    out_path = "avi-ascii.svg"
    if not os.path.exists(img_path):
        print(f"[!] Error: {img_path} not found. Run scripts/prep_photo.py first.")
        sys.exit(1)

    print("[*] Converting image to centered ASCII art...")
    lines = generate_ascii_art(img_path, cols=96, rows=56)
    create_ascii_svg(lines, out_path)


if __name__ == "__main__":
    main()
