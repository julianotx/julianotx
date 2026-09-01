#!/usr/bin/env python3
"""
scripts/make_tech_stack_svg.py
Generates a stunning animated tech-stack visualization SVG (tech-stack.svg).

Visual: Terminal window with animated skill bars that fill from left to right,
grouped by category (Frontend, Backend, Data & Tools), with glowing accent
colors and a sleek dark terminal aesthetic.

Width: 860px (matches heatmap for perfect alignment).
"""

import html
import os
import sys


def generate_tech_stack_svg(output_path: str = "tech-stack.svg", is_static: bool = False):
    svg_w = 860
    bar_h = 14
    bar_gap = 28
    section_gap = 16
    col_gap = 32
    col_w = (svg_w - 48 - col_gap) // 2  # two-column layout

    # ── Skill definitions ────────────────────────────────────────
    # (name, percentage, color)
    col_left = [
        ("section", "Frontend", "#58a6ff"),
        ("Next.js / React",   88, "#61dafb"),
        ("TypeScript",        85, "#3178c6"),
        ("HTML / CSS",        92, "#e34f26"),
        ("Tailwind CSS",      78, "#38bdf8"),
        ("section", "Backend", "#7ee787"),
        ("Node.js",           80, "#339933"),
        ("Python",            82, "#3776ab"),
        ("PostgreSQL / SQL",  85, "#336791"),
        ("Supabase",          78, "#3ecf8e"),
    ]

    col_right = [
        ("section", "Data &amp; BI", "#d29922"),
        ("Power BI",          75, "#f2c811"),
        ("Data Analysis",     80, "#e06c75"),
        ("SQL Queries",       88, "#336791"),
        ("Excel / Sheets",    85, "#217346"),
        ("section", "DevOps &amp; Tools", "#a371f7"),
        ("Git / GitHub",      90, "#f05032"),
        ("CI/CD (Actions)",   72, "#2088ff"),
        ("Docker",            65, "#2496ed"),
        ("Vercel / Deploy",   82, "#f0f0f0"),
    ]

    FONT_MONO = "'Consolas','Cascadia Code','Fira Code','Courier New',monospace"
    FONT_SYS = "-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif"

    # Calculate SVG height
    def calc_height(items):
        h = 0
        for item in items:
            if item[0] == "section":
                h += section_gap + 18
            else:
                h += bar_gap
        return h

    left_h = calc_height(col_left)
    right_h = calc_height(col_right)
    content_h = max(left_h, right_h)
    pad_top = 64
    pad_bottom = 24
    svg_h = pad_top + content_h + pad_bottom

    # ── Animation CSS ────────────────────────────────────────────
    anim_css = ""
    if not is_static:
        anim_css = """
      @keyframes barFill { 0% { width: 0; } 100% { width: var(--tw); } }
      @keyframes fadeSlide { 0% { opacity: 0; transform: translateX(-10px); } 100% { opacity: 1; transform: translateX(0); } }
      .bar-fill { width: 0; }
      .skill-row { opacity: 0; }
"""

    css_block = f"""
      text {{ font-family: {FONT_MONO}; font-size: 11.5px; fill: #c9d1d9; }}
      .section-title {{ font-size: 12.5px; font-weight: 700; }}
      .pct-label {{ font-size: 10px; fill: #8b949e; }}
      {anim_css}
    """

    # ── Build skill bars ─────────────────────────────────────────
    elements = []
    anim_idx = 0

    def render_column(items, start_x, max_bar_w):
        nonlocal anim_idx
        col_elements = []
        cur_y = pad_top

        for item in items:
            if item[0] == "section":
                _, title, color = item
                cur_y += section_gap
                delay = 0.08 + anim_idx * 0.04
                anim_idx += 1

                cls = sty = smil = ""
                if not is_static:
                    cls = ' class="skill-row"'
                    sty = f' style="animation: fadeSlide 0.3s ease {delay:.2f}s forwards;"'
                    smil = (f'<animate attributeName="opacity" from="0" to="1" '
                            f'dur="0.3s" begin="{delay:.2f}s" fill="freeze"/>')

                col_elements.append(
                    f'    <g{cls}{sty}>{smil}'
                    f'<text x="{start_x}" y="{cur_y}" fill="{color}" '
                    f'class="section-title">{title}</text></g>'
                )
                cur_y += 18
            else:
                name, pct, color = item
                delay = 0.08 + anim_idx * 0.04
                anim_idx += 1
                bar_w = int(max_bar_w * pct / 100)
                label_x = start_x
                bar_x = start_x + 145
                actual_bar_w = max_bar_w - 145
                fill_w = int(actual_bar_w * pct / 100)

                # Row animation
                cls = sty = smil = ""
                if not is_static:
                    cls = ' class="skill-row"'
                    sty = f' style="animation: fadeSlide 0.3s ease {delay:.2f}s forwards;"'
                    smil = (f'<animate attributeName="opacity" from="0" to="1" '
                            f'dur="0.3s" begin="{delay:.2f}s" fill="freeze"/>')

                # Bar background (track)
                track = (f'<rect x="{bar_x}" y="{cur_y - 10}" '
                         f'width="{actual_bar_w}" height="{bar_h}" '
                         f'rx="4" fill="#21262d"/>')

                # Bar fill (animated)
                bar_delay = delay + 0.15
                if not is_static:
                    bar_fill = (
                        f'<rect class="bar-fill" x="{bar_x}" y="{cur_y - 10}" '
                        f'width="0" height="{bar_h}" rx="4" fill="{color}" opacity="0.85">'
                        f'<animate attributeName="width" from="0" to="{fill_w}" '
                        f'dur="0.6s" begin="{bar_delay:.2f}s" fill="freeze" '
                        f'calcMode="spline" keySplines="0.25 0.1 0.25 1"/>'
                        f'</rect>'
                    )
                else:
                    bar_fill = (
                        f'<rect x="{bar_x}" y="{cur_y - 10}" '
                        f'width="{fill_w}" height="{bar_h}" rx="4" '
                        f'fill="{color}" opacity="0.85"/>'
                    )

                # Glow effect (subtle)
                glow = (f'<rect x="{bar_x}" y="{cur_y - 10}" '
                        f'width="{fill_w}" height="{bar_h}" rx="4" '
                        f'fill="{color}" opacity="0.15" filter="url(#glow)">'
                        f'<animate attributeName="width" from="0" to="{fill_w}" '
                        f'dur="0.6s" begin="{bar_delay:.2f}s" fill="freeze"/>'
                        f'</rect>' if not is_static else '')

                # Percentage label
                pct_x = bar_x + actual_bar_w + 8
                pct_label = (f'<text x="{pct_x}" y="{cur_y}" '
                             f'class="pct-label">{pct}%</text>')

                # Skill name
                name_el = f'<text x="{label_x}" y="{cur_y}" fill="#c9d1d9">{name}</text>'

                col_elements.append(
                    f'    <g{cls}{sty}>{smil}'
                    f'{name_el}{track}{bar_fill}{glow}{pct_label}</g>'
                )
                cur_y += bar_gap

        return col_elements

    left_x = 24
    right_x = 24 + col_w + col_gap
    max_bar_w = col_w - 30

    left_els = render_column(col_left, left_x, max_bar_w)
    right_els = render_column(col_right, right_x, max_bar_w)
    elements = left_els + right_els

    body_str = "\n".join(elements)

    # ── Glow filter ──────────────────────────────────────────────
    glow_filter = """
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>"""

    # ── Separator line between columns ───────────────────────────
    sep_x = left_x + col_w + col_gap // 2
    separator = (f'<line x1="{sep_x}" y1="{pad_top - 5}" '
                 f'x2="{sep_x}" y2="{svg_h - pad_bottom}" '
                 f'stroke="#21262d" stroke-width="1" stroke-dasharray="4,4"/>')

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">
  <defs>
    <style>{css_block}</style>
    {glow_filter}
  </defs>

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
  <text x="{svg_w//2}" y="19" text-anchor="middle" fill="#8b949e"
        font-family="{FONT_SYS}" font-size="11px" font-weight="500">julianotx@github ~ cat skills.json</text>

  <!-- Column Separator -->
  {separator}

  <!-- Skill Bars -->
{body_str}
</svg>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)

    tag = "static" if is_static else "animated"
    print(f"[+] Tech Stack SVG ({tag}): {output_path} ({svg_w}x{svg_h})")


def main():
    is_static = os.environ.get("STATIC", "0").lower() in ("1", "true", "yes")
    out_path = sys.argv[1] if len(sys.argv) > 1 else "tech-stack.svg"
    generate_tech_stack_svg(out_path, is_static)


if __name__ == "__main__":
    main()
