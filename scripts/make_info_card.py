#!/usr/bin/env python3
"""
scripts/make_info_card.py
Gera o SVG de informações do perfil no estilo neofetch (info-card.svg).
- Barra de título de terminal com botões coloridos
- Prompt interativo: julianotx@github ~ $ neofetch
- Dados reais: Now, Prev, Stack, Highlights, OS, etc.
- Paleta de blocos de cor ANSI do terminal (███)
- Animação staggered de fade + slide-in
- Suporte a flag de ambiente STATIC=1 para versão congelada sem animação
- Salva como info-card.svg na raiz
"""

import os
import sys
import html

def generate_info_card_svg(output_path: str = "info-card.svg", is_static: bool = False):
    svg_w = 680
    svg_h = 570

    # Itens do Neofetch com dados autênticos do usuário
    data_items = [
        ("title", "julianotx@github", "#58a6ff"),
        ("sep", "-" * 42, "#30363d"),
        ("OS", "GitHub / Windows 11 x86_64", "#79c0ff"),
        ("Host", "julianotx.dev (Portfolio Terminal)", "#79c0ff"),
        ("Now", "Analista de Sistemas / Dados em transição para BI", "#7ee787"),
        ("Prev", "Prevenção de Perdas (Magalog) | Conf. de Carga (GFL)", "#d29922"),
        ("Stack", "Next.js, TypeScript, Supabase, PostgreSQL, Python, Power BI, SQL", "#a371f7"),
        ("Highlights", "Formado em ADS (Anhanguera, 2026) | Automação & No-Code", "#f0883e"),
        ("Uptime", "Curioso incansável, focado em impacto & produto", "#58a6ff"),
        ("Shell", "pwsh 7.6.5 with oh-my-posh", "#79c0ff"),
        ("Status", "Aberto a novas oportunidades em BI & Engenharia de Dados", "#56d364"),
    ]

    # Blocos de cor ANSI padrão neofetch
    ansi_colors_1 = ["#0d1117", "#ff7b72", "#7ee787", "#f2cc60", "#79c0ff", "#d2a8ff", "#56d364", "#c9d1d9"]
    ansi_colors_2 = ["#484f58", "#ffa198", "#56d364", "#e3b341", "#a5d6ff", "#e2c5ff", "#39d353", "#f0f6fc"]

    start_delay = 0.15
    stagger = 0.08
    duration = 0.35

    css_rules = ["""
      .card-bg { fill: #0d1117; stroke: #30363d; stroke-width: 1.5; rx: 10px; }
      .card-header { fill: #161b22; }
      .header-title { fill: #8b949e; font-family: 'Segoe UI', -apple-system, sans-serif; font-size: 11px; font-weight: 500; }
      .mono-font {
        font-family: 'Consolas', 'Cascadia Code', 'Fira Code', 'Courier New', monospace;
        font-size: 12.5px;
      }
      .prompt-user { fill: #58a6ff; font-weight: 600; }
      .prompt-at { fill: #8b949e; }
      .prompt-host { fill: #bc8cff; font-weight: 600; }
      .prompt-dir { fill: #7ee787; }
      .prompt-cmd { fill: #f0f6fc; }
      .label-key { fill: #58a6ff; font-weight: 600; }
      .label-colon { fill: #8b949e; }
      .label-val { fill: #c9d1d9; }
    """]

    if not is_static:
        css_rules.append("""
      @keyframes slideInFade {
        0% { opacity: 0; transform: translateY(8px); }
        100% { opacity: 1; transform: translateY(0); }
      }
      .animated-row {
        opacity: 0;
        animation: slideInFade 0.35s cubic-bezier(0.2, 0.0, 0.35, 1) forwards;
      }
        """)

    body_elements = []

    # Linha do Prompt
    prompt_y = 65
    prompt_delay = start_delay
    delay_style = f"style=\"animation-delay: {prompt_delay:.2f}s;\"" if not is_static else ""
    anim_class = "animated-row" if not is_static else ""

    smil_prompt = ""
    if not is_static:
        smil_prompt = f"""
      <animate attributeName="opacity" from="0" to="1" dur="{duration}s" begin="{prompt_delay:.2f}s" fill="freeze" />
      <animateTransform attributeName="transform" type="translate" from="0, 8" to="0, 0" dur="{duration}s" begin="{prompt_delay:.2f}s" fill="freeze" />"""

    body_elements.append(f"""
    <g class="{anim_class}" {delay_style}>{smil_prompt}
      <text x="24" y="{prompt_y}" class="mono-font">
        <tspan class="prompt-user">julianotx</tspan>
        <tspan class="prompt-at">@</tspan>
        <tspan class="prompt-host">github</tspan>
        <tspan class="label-val">:</tspan>
        <tspan class="prompt-dir">~</tspan>
        <tspan class="label-val">$ </tspan>
        <tspan class="prompt-cmd">neofetch --profile</tspan>
      </text>
    </g>""")

    # Linhas dos Itens
    cur_y = 100
    line_step = 28

    for idx, (key, val, col) in enumerate(data_items):
        item_delay = start_delay + (idx + 1) * stagger
        delay_style = f"style=\"animation-delay: {item_delay:.2f}s;\"" if not is_static else ""
        
        smil_item = ""
        if not is_static:
            smil_item = f"""
      <animate attributeName="opacity" from="0" to="1" dur="{duration}s" begin="{item_delay:.2f}s" fill="freeze" />
      <animateTransform attributeName="transform" type="translate" from="0, 8" to="0, 0" dur="{duration}s" begin="{item_delay:.2f}s" fill="freeze" />"""

        if key == "title":
            row_html = f"""
    <g class="{anim_class}" {delay_style}>{smil_item}
      <text x="24" y="{cur_y}" class="mono-font" font-weight="700" font-size="14px" fill="{col}">
        {html.escape(val)}
      </text>
    </g>"""
            cur_y += 20
        elif key == "sep":
            row_html = f"""
    <g class="{anim_class}" {delay_style}>{smil_item}
      <text x="24" y="{cur_y}" class="mono-font" fill="{col}">
        {html.escape(val)}
      </text>
    </g>"""
            cur_y += 24
        else:
            # Quebra inteligente para itens longos (como Stack e Prev) para não transbordar o card
            escaped_val = html.escape(val)
            row_html = f"""
    <g class="{anim_class}" {delay_style}>{smil_item}
      <text x="24" y="{cur_y}" class="mono-font">
        <tspan class="label-key" fill="{col}">{html.escape(key)}</tspan>
        <tspan class="label-colon">: </tspan>
        <tspan class="label-val">{escaped_val}</tspan>
      </text>
    </g>"""
            cur_y += line_step

        body_elements.append(row_html)

    # Blocos de Cor ANSI (Neofetch color blocks)
    blocks_delay = start_delay + (len(data_items) + 2) * stagger
    delay_style = f"style=\"animation-delay: {blocks_delay:.2f}s;\"" if not is_static else ""
    smil_blocks = ""
    if not is_static:
        smil_blocks = f"""
      <animate attributeName="opacity" from="0" to="1" dur="{duration}s" begin="{blocks_delay:.2f}s" fill="freeze" />
      <animateTransform attributeName="transform" type="translate" from="0, 8" to="0, 0" dur="{duration}s" begin="{blocks_delay:.2f}s" fill="freeze" />"""

    block_w = 26
    block_h = 13
    block_start_x = 24
    block_y_1 = cur_y + 12
    block_y_2 = block_y_1 + block_h + 3

    rects_1 = []
    rects_2 = []
    for i, c in enumerate(ansi_colors_1):
        rects_1.append(f'<rect x="{block_start_x + i * (block_w + 5)}" y="{block_y_1}" width="{block_w}" height="{block_h}" rx="2" fill="{c}" />')
    for i, c in enumerate(ansi_colors_2):
        rects_2.append(f'<rect x="{block_start_x + i * (block_w + 5)}" y="{block_y_2}" width="{block_w}" height="{block_h}" rx="2" fill="{c}" />')

    body_elements.append(f"""
    <g class="{anim_class}" {delay_style}>{smil_blocks}
      {' '.join(rects_1)}
      {' '.join(rects_2)}
    </g>""")

    css_str = "\n".join(css_rules)
    body_str = "\n".join(body_elements)

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">
  <defs>
    <style>
{css_str}
    </style>
  </defs>

  <!-- Terminal Window Background -->
  <rect x="1" y="1" width="{svg_w - 2}" height="{svg_h - 2}" class="card-bg" />

  <!-- Terminal Header Bar -->
  <path d="M 1,11 A 10,10 0 0,1 11,1 L {svg_w - 11},1 A 10,10 0 0,1 {svg_w - 1},11 L {svg_w - 1},30 L 1,30 Z" class="card-header" />
  <line x1="1" y1="30" x2="{svg_w - 1}" y2="30" stroke="#30363d" stroke-width="1" />

  <!-- Terminal Window Buttons -->
  <circle cx="18" cy="15" r="4.5" fill="#ff5f56" />
  <circle cx="32" cy="15" r="4.5" fill="#ffbd2e" />
  <circle cx="46" cy="15" r="4.5" fill="#27c93f" />

  <!-- Header Title -->
  <text x="{svg_w // 2}" y="19" text-anchor="middle" class="header-title">julianotx@github ~ neofetch</text>

  <!-- Neofetch Content Body -->
{body_str}
</svg>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)

    status_str = "estático" if is_static else "animado"
    print(f"[+] Info Card SVG ({status_str}) gerado com sucesso: {output_path} ({svg_w}x{svg_h})")

def main():
    is_static = os.environ.get("STATIC", "0").lower() in ("1", "true", "yes")
    out_path = sys.argv[1] if len(sys.argv) > 1 else "info-card.svg"
    generate_info_card_svg(out_path, is_static)

if __name__ == "__main__":
    main()
