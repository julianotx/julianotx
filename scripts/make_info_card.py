#!/usr/bin/env python3
"""
scripts/make_info_card.py
Generates the neofetch-style profile information card SVG (info-card.svg).

Reads dynamic GitHub stats from data/github_stats.json (if available) to
show live repo/follower/star counts. Falls back to static values when the
stats file is missing (e.g. first local run before the workflow populates it).

All text uses inline fill attributes for maximum GitHub SVG proxy compatibility.
"""

import os
import sys
import json
import html
from pathlib import Path


def load_github_stats() -> dict:
    """Load dynamic stats from data/github_stats.json if it exists."""
    p = Path("data/github_stats.json")
    if p.exists():
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def generate_info_card_svg(output_path: str = "info-card.svg", is_static: bool = False):
    svg_w = 490
    svg_h = 480

    stats = load_github_stats()
    repos = stats.get("public_repos", "1")
    followers = stats.get("followers", "3")
    stars_given = stats.get("stars_given", "15")

    # Professional English profile data — NO "Prev" field
    data_items = [
        ("title", "julianotx@github", "#58a6ff"),
        ("sep",   "-" * 34,           "#30363d"),
        ("OS",       "GitHub / Windows 11 x86_64",                          "#79c0ff"),
        ("Role",     "System Analyst & Full Stack Developer",               "#7ee787"),
        ("Degree",   "Associate Degree in System Analysis & Dev",           "#d29922"),
        ("Location", "Sao Paulo, SP - Brazil",                              "#79c0ff"),
        ("Stack",    "Next.js, TS, React, Supabase, Python, SQL",           "#a371f7"),
        ("Focus",    "Full-Stack Apps, Data Pipelines & Automation",        "#58a6ff"),
        ("Shell",    "pwsh 7.6.5 + oh-my-posh",                            "#79c0ff"),
        ("Repos",    str(repos),                                            "#7ee787"),
        ("Stars",    str(stars_given),                                      "#f2cc60"),
        ("Followers", str(followers),                                       "#d2a8ff"),
        ("Status",   "Open to new opportunities",                           "#56d364"),
    ]

    ansi_colors_1 = ["#0d1117", "#ff7b72", "#7ee787", "#f2cc60",
                     "#79c0ff", "#d2a8ff", "#56d364", "#c9d1d9"]
    ansi_colors_2 = ["#484f58", "#ffa198", "#56d364", "#e3b341",
                     "#a5d6ff", "#e2c5ff", "#39d353", "#f0f6fc"]

    start_delay = 0.10
    stagger     = 0.055
    duration    = 0.28

    COL_VAL   = "#c9d1d9"
    COL_COLON = "#8b949e"
    COL_CMD   = "#f0f6fc"
    COL_USER  = "#58a6ff"
    COL_AT    = "#8b949e"
    COL_HOST  = "#bc8cff"
    COL_DIR   = "#7ee787"
    COL_TITLE = "#8b949e"
    FONT_MONO = "'Consolas','Cascadia Code','Fira Code','Courier New',monospace"
    FONT_SYS  = "-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif"

    anim_css = ""
    if not is_static:
        anim_css = """
      @keyframes slideIn {
        0%   { opacity: 0; transform: translateY(8px); }
        100% { opacity: 1; transform: translateY(0);   }
      }
      .anim { opacity: 0; }
"""

    css_block = f"""
      text {{ font-family: {FONT_MONO}; font-size: 11.8px; }}
      {anim_css}
    """

    body = []

    def anim_attrs(delay: float):
        if is_static:
            return "", "", ""
        cls = ' class="anim"'
        sty = f' style="animation: slideIn {duration}s ease {delay:.2f}s forwards;"'
        smil = (f'<animate attributeName="opacity" from="0" to="1" '
                f'dur="{duration}s" begin="{delay:.2f}s" fill="freeze"/>'
                f'<animateTransform attributeName="transform" type="translate" '
                f'from="0,8" to="0,0" dur="{duration}s" begin="{delay:.2f}s" fill="freeze"/>')
        return cls, sty, smil

    # Prompt line
    prompt_y = 54
    cls, sty, smil = anim_attrs(start_delay)
    body.append(f"""    <g{cls}{sty}>{smil}
      <text x="20" y="{prompt_y}">
        <tspan fill="{COL_USER}" font-weight="600">julianotx</tspan>
        <tspan fill="{COL_AT}">@</tspan>
        <tspan fill="{COL_HOST}" font-weight="600">github</tspan>
        <tspan fill="{COL_VAL}">:</tspan>
        <tspan fill="{COL_DIR}">~</tspan>
        <tspan fill="{COL_VAL}"> $ </tspan>
        <tspan fill="{COL_CMD}">neofetch</tspan>
      </text>
    </g>""")

    # Data rows
    cur_y = 84
    line_step = 23

    for idx, (key, val, col) in enumerate(data_items):
        delay = start_delay + (idx + 1) * stagger
        cls, sty, smil = anim_attrs(delay)
        escaped = html.escape(val)

        if key == "title":
            body.append(f"""    <g{cls}{sty}>{smil}
      <text x="20" y="{cur_y}" font-weight="700" font-size="13px" fill="{col}">{escaped}</text>
    </g>""")
            cur_y += 16
        elif key == "sep":
            body.append(f"""    <g{cls}{sty}>{smil}
      <text x="20" y="{cur_y}" fill="{col}">{escaped}</text>
    </g>""")
            cur_y += 18
        else:
            body.append(f"""    <g{cls}{sty}>{smil}
      <text x="20" y="{cur_y}">
        <tspan fill="{col}" font-weight="600">{html.escape(key)}</tspan>
        <tspan fill="{COL_COLON}"> : </tspan>
        <tspan fill="{COL_VAL}">{escaped}</tspan>
      </text>
    </g>""")
            cur_y += line_step

    # ANSI colour blocks
    blocks_delay = start_delay + (len(data_items) + 2) * stagger
    cls, sty, smil = anim_attrs(blocks_delay)
    bw, bh, bx = 22, 12, 20
    by1 = cur_y + 12
    by2 = by1 + bh + 3
    gap = bw + 4

    rects_1 = " ".join(
        f'<rect x="{bx + i * gap}" y="{by1}" width="{bw}" height="{bh}" rx="2" fill="{c}"/>'
        for i, c in enumerate(ansi_colors_1))
    rects_2 = " ".join(
        f'<rect x="{bx + i * gap}" y="{by2}" width="{bw}" height="{bh}" rx="2" fill="{c}"/>'
        for i, c in enumerate(ansi_colors_2))

    body.append(f"""    <g{cls}{sty}>{smil}
      {rects_1}
      {rects_2}
    </g>""")

    body_str = "\n".join(body)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">
  <defs><style>{css_block}</style></defs>

  <!-- Terminal background -->
  <rect x="1" y="1" width="{svg_w-2}" height="{svg_h-2}" rx="10" fill="#0d1117" stroke="#30363d" stroke-width="1.5"/>

  <!-- Header bar -->
  <path d="M1,11 A10,10 0 0,1 11,1 L{svg_w-11},1 A10,10 0 0,1 {svg_w-1},11 L{svg_w-1},30 L1,30Z" fill="#161b22"/>
  <line x1="1" y1="30" x2="{svg_w-1}" y2="30" stroke="#30363d" stroke-width="1"/>

  <!-- Window buttons -->
  <circle cx="18" cy="15" r="4.5" fill="#ff5f56"/>
  <circle cx="32" cy="15" r="4.5" fill="#ffbd2e"/>
  <circle cx="46" cy="15" r="4.5" fill="#27c93f"/>

  <!-- Title -->
  <text x="{svg_w//2}" y="19" text-anchor="middle" fill="{COL_TITLE}"
        font-family="{FONT_SYS}" font-size="11px" font-weight="500">julianotx@github ~ neofetch</text>

  <!-- Body -->
{body_str}
</svg>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)

    tag = "static" if is_static else "animated"
    print(f"[+] Info Card SVG ({tag}): {output_path} ({svg_w}x{svg_h})")


def main():
    is_static = os.environ.get("STATIC", "0").lower() in ("1", "true", "yes")
    out_path = sys.argv[1] if len(sys.argv) > 1 else "info-card.svg"
    generate_info_card_svg(out_path, is_static)


if __name__ == "__main__":
    main()
