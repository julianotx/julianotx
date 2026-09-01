#!/usr/bin/env python3
"""
scripts/make_ascii_svg.py
Gera o SVG animado do retrato em arte ASCII (avi-ascii.svg).
- Reamostra source-prepped.png para uma grade de ~96x53 caracteres
- Mapeia com a rampa: RAMP = " .:-=+*cs#%@"
- Monocromático (cinza claro #c9d1d9 sobre terminal #0d1117)
- Efeito digitando progressivo via clipPath animado (SMIL + CSS keyframes)
- Toca uma única vez e congela (sem loop)
"""

import sys
import os
import html
from pathlib import Path
import numpy as np
from PIL import Image

RAMP = " .:-=+*cs#%@"

def generate_ascii_art(image_path: str, cols: int = 96, rows: int = 53):
    img = Image.open(image_path)
    
    # Detecção inteligente da caixa delimitadora do conteúdo
    arr_full = np.array(img)
    non_white = np.where(arr_full < 250)
    if len(non_white[0]) > 0:
        min_y = max(0, int(non_white[0].min()) - 25)
        max_y = int(non_white[0].max())
        img_cropped = img.crop((0, min_y, img.size[0], max_y))
    else:
        img_cropped = img

    # Reamostragem com interpolação LANCZOS de alta qualidade
    small = img_cropped.resize((cols, rows), Image.Resampling.LANCZOS)
    arr = np.array(small)
    ramp_len = len(RAMP)

    lines = []
    for r in range(rows):
        line_chars = []
        for c in range(cols):
            val = int(arr[r, c])
            # val = 255 (fundo branco) -> 0 (espaço)
            # val = 0 (escuro) -> ramp_len - 1 (@)
            idx = int((255 - val) / 255.0 * (ramp_len - 1))
            idx = max(0, min(ramp_len - 1, idx))
            line_chars.append(RAMP[idx])
        lines.append("".join(line_chars))

    return lines

def create_ascii_svg(lines: list, output_path: str = "avi-ascii.svg"):
    rows = len(lines)
    cols = len(lines[0])

    # Dimensões da célula de caractere (monospace)
    char_w = 5.6
    line_h = 10.8
    pad_x = 18
    pad_top = 44
    pad_bottom = 20

    content_w = cols * char_w
    content_h = rows * line_h
    svg_w = int(content_w + pad_x * 2)
    svg_h = int(content_h + pad_top + pad_bottom)

    stagger = 0.038
    duration = 0.22

    # Construção do CSS e SMIL
    css_rules = []
    clips = []
    text_elements = []

    css_rules.append("""
      @keyframes revealWidth {
        0% { width: 0px; }
        100% { width: __CW__px; }
      }
      .term-bg { fill: #0d1117; stroke: #30363d; stroke-width: 1.5; rx: 10px; }
      .term-header { fill: #161b22; }
      .term-title { fill: #8b949e; font-family: 'Segoe UI', -apple-system, sans-serif; font-size: 11px; font-weight: 500; }
      .ascii-text {
        fill: #c9d1d9;
        font-family: 'Consolas', 'Cascadia Code', 'Fira Code', 'Courier New', monospace;
        font-size: 8.8px;
        letter-spacing: 0px;
        white-space: pre;
      }
    """.replace("__CW__", str(int(content_w + 10))))

    for i, line in enumerate(lines):
        clip_id = f"cp-{i}"
        y_pos = pad_top + i * line_h
        begin_sec = 0.12 + i * stagger

        css_rules.append(f"""
      .clip-rect-{i} {{
        width: 0px;
        animation: revealWidth {duration}s cubic-bezier(0.2, 0.0, 0.38, 0.9) {begin_sec:.3f}s forwards;
      }}""")

        # ClipPath com suporte dual: CSS class + SMIL <animate>
        clip_svg = f"""    <clipPath id="{clip_id}">
      <rect class="clip-rect-{i}" x="{pad_x - 2}" y="{y_pos - 8}" width="0" height="{line_h + 2}">
        <animate attributeName="width" from="0" to="{int(content_w + 10)}" dur="{duration}s" begin="{begin_sec:.3f}s" fill="freeze" />
      </rect>
    </clipPath>"""
        clips.append(clip_svg)

        escaped_line = html.escape(line)
        text_el = f"""    <g clip-path="url(#{clip_id})">
      <text x="{pad_x}" y="{y_pos}" class="ascii-text" xml:space="preserve">{escaped_line}</text>
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

  <!-- ASCII Lines with typing animation -->
{texts_str}
</svg>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)

    print(f"[+] ASCII SVG gerado com sucesso: {output_path} ({svg_w}x{svg_h})")

def main():
    img_path = "source-prepped.png"
    out_path = "avi-ascii.svg"
    if not os.path.exists(img_path):
        print(f"[!] Erro: {img_path} não encontrado. Execute scripts/prep_photo.py primeiro.")
        sys.exit(1)

    print("[*] Convertendo imagem em ASCII...")
    lines = generate_ascii_art(img_path, cols=96, rows=53)
    create_ascii_svg(lines, out_path)

if __name__ == "__main__":
    main()
