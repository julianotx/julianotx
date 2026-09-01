#!/usr/bin/env python3
"""
scripts/render_heatmap_svg.py
Renderiza a grade clássica de contribuições do GitHub em SVG animado (contrib-heatmap.svg).
- Lê data/contributions.json
- Grade 53 semanas x 7 dias com caixinhas arredondadas (rx="2.5")
- Paleta oficial: ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
- Animação de entrada diagonal (linha após linha / coluna em onda fluida), toca 1x e congela
- Legenda "Less -> More" + estatísticas reais no rodapé
- Largura exata de 860px para alinhamento perfeito com os 370 + 490 = 860 da seção whoami
"""

import sys
import json
import html
from datetime import datetime, date, timedelta
from pathlib import Path

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

MONTH_NAMES = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
DAY_NAMES = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]

def load_data(json_path: str = "data/contributions.json"):
    p = Path(json_path)
    if not p.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {json_path}")
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def render_heatmap(data: dict, output_path: str = "contrib-heatmap.svg"):
    svg_w = 860
    svg_h = 225

    days_list = data.get("days", [])
    stats = data.get("stats", {})
    total_contribs = stats.get("total", sum(d.get("count", 0) for d in days_list))
    current_streak = stats.get("current_streak", 0)
    longest_streak = stats.get("longest_streak", 0)

    # Mapear dias por data
    day_map = {d["date"]: d for d in days_list}

    # Organizar os últimos 371 dias em 53 semanas de 7 dias
    # Encontrar a última data disponível
    if days_list:
        last_date = datetime.strptime(days_list[-1]["date"], "%Y-%m-%d").date()
    else:
        last_date = date.today()

    # O último dia do grid deve ser alinhado com o dia da semana
    # No GitHub, as linhas vão de 0 (Domingo) a 6 (Sábado)
    # Python weekday(): Segunda=0 ... Domingo=6.
    # Convertemos para Domingo=0 ... Sábado=6:
    # sun_weekday = (py_weekday + 1) % 7
    last_sun_weekday = (last_date.weekday() + 1) % 7
    
    # Queremos 53 colunas (semanas). O fim da última semana é last_date + (6 - last_sun_weekday) dias
    end_of_grid = last_date + timedelta(days=(6 - last_sun_weekday))
    start_of_grid = end_of_grid - timedelta(days=53 * 7 - 1)

    # Coordenadas do grid
    grid_left = 50
    grid_top = 68
    cell_size = 11.2
    cell_gap = 3.2
    col_step = cell_size + cell_gap
    row_step = cell_size + cell_gap

    # Mapeamento dos meses para os rótulos superiores
    month_labels = []
    seen_months = set()

    cells_svg = []
    css_cells = []

    # Duração e tempos de animação diagonal
    base_delay = 0.12
    diag_factor = 0.016
    anim_dur = 0.32

    for col in range(53):
        col_x = grid_left + col * col_step
        col_start_date = start_of_grid + timedelta(days=col * 7)
        
        # Verificar se o mês mudou nesta semana
        m_idx = col_start_date.month
        ym_key = f"{col_start_date.year}-{m_idx}"
        if ym_key not in seen_months and col < 52:
            seen_months.add(ym_key)
            m_name = MONTH_NAMES[m_idx - 1]
            month_labels.append((col_x, m_name))

        for row in range(7):
            cur_date = col_start_date + timedelta(days=row)
            date_str = cur_date.strftime("%Y-%m-%d")
            row_y = grid_top + row * row_step

            # Buscar dados do dia
            d_info = day_map.get(date_str)
            if d_info is not None:
                count = d_info.get("count", 0)
                level = d_info.get("level", 0)
                # Garantir índice na paleta
                if count == 0:
                    color = PALETTE[0]
                    stroke_style = 'stroke="#21262d" stroke-width="0.7"'
                else:
                    color_idx = min(len(PALETTE) - 1, max(1, level))
                    color = PALETTE[color_idx]
                    stroke_style = 'stroke="rgba(255,255,255,0.08)" stroke-width="0.5"'
            else:
                # Fora do intervalo de dados reais (futuro ou passado)
                color = "#161b22"
                stroke_style = 'stroke="#21262d" stroke-width="0.7"'
                count = 0

            # Diagonal delay: (col + row)
            diag_val = col + row
            delay = base_delay + diag_val * diag_factor
            cid = f"c-{col}-{row}"

            css_cells.append(f"""
      .{cid} {{
        opacity: 0;
        animation: cellFadeIn {anim_dur}s ease-out {delay:.3f}s forwards;
      }}""")

            cell_el = f"""    <rect class="cell {cid}" x="{col_x:.1f}" y="{row_y:.1f}" width="{cell_size}" height="{cell_size}" rx="2.5" fill="{color}" {stroke_style}>
      <animate attributeName="opacity" from="0" to="1" dur="{anim_dur}s" begin="{delay:.3f}s" fill="freeze" />
      <animateTransform attributeName="transform" type="translate" from="0, 4" to="0, 0" dur="{anim_dur}s" begin="{delay:.3f}s" fill="freeze" />
    </rect>"""
            cells_svg.append(cell_el)

    # Rótulos dos meses
    months_svg = []
    for mx, mname in month_labels:
        months_svg.append(f'<text x="{mx:.1f}" y="{grid_top - 9}" class="axis-label">{mname}</text>')

    # Rótulos dos dias (Seg, Qua, Sex)
    days_labels_svg = []
    day_indices = [(1, "Seg"), (3, "Qua"), (5, "Sex")]
    for d_idx, d_name in day_indices:
        dy = grid_top + d_idx * row_step + 9.2
        days_labels_svg.append(f'<text x="{grid_left - 8}" y="{dy:.1f}" text-anchor="end" class="axis-label">{d_name}</text>')

    # Legenda "Less -> More"
    legend_svg = []
    leg_x = svg_w - 50 - len(PALETTE) * 14 - 80
    leg_y = grid_top + 7 * row_step + 24

    legend_svg.append(f'<text x="{leg_x - 6}" y="{leg_y + 9}" text-anchor="end" class="footer-label">Menos</text>')
    for i, c in enumerate(PALETTE):
        lx = leg_x + i * 14
        stroke_leg = 'stroke="#21262d" stroke-width="0.7"' if i == 0 else ''
        legend_svg.append(f'<rect x="{lx}" y="{leg_y}" width="10" height="10" rx="2" fill="{c}" {stroke_leg} />')
    legend_svg.append(f'<text x="{leg_x + len(PALETTE) * 14 + 6}" y="{leg_y + 9}" class="footer-label">Mais</text>')

    # Rodapé estatístico à esquerda
    formatted_total = f"{total_contribs:,}".replace(",", ".")
    footer_text = f"<b>{formatted_total}</b> contribuições no último ano &nbsp;•&nbsp; Streak Atual: <b>{current_streak} dias</b> &nbsp;•&nbsp; Recorde: <b>{longest_streak} dias</b>"

    css_str = f"""
      @keyframes cellFadeIn {{
        0% {{ opacity: 0; transform: translateY(4px); }}
        100% {{ opacity: 1; transform: translateY(0); }}
      }}
      .term-bg {{ fill: #0d1117; stroke: #30363d; stroke-width: 1.5; rx: 10px; }}
      .term-header {{ fill: #161b22; }}
      .term-title {{ fill: #8b949e; font-family: 'Segoe UI', -apple-system, sans-serif; font-size: 11px; font-weight: 500; }}
      .axis-label {{ fill: #7d8590; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 10px; }}
      .footer-label {{ fill: #7d8590; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 10.5px; }}
      .footer-stat {{ fill: #c9d1d9; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 11.5px; }}
      .footer-stat-hl {{ fill: #58a6ff; font-weight: 600; }}
      {"".join(css_cells)}
    """

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">
  <defs>
    <style>
{css_str}
    </style>
  </defs>

  <!-- Terminal Card Background -->
  <rect x="1" y="1" width="{svg_w - 2}" height="{svg_h - 2}" class="term-bg" />

  <!-- Terminal Header Bar -->
  <path d="M 1,11 A 10,10 0 0,1 11,1 L {svg_w - 11},1 A 10,10 0 0,1 {svg_w - 1},11 L {svg_w - 1},30 L 1,30 Z" class="term-header" />
  <line x1="1" y1="30" x2="{svg_w - 1}" y2="30" stroke="#30363d" stroke-width="1" />

  <!-- Terminal Window Buttons -->
  <circle cx="18" cy="15" r="4.5" fill="#ff5f56" />
  <circle cx="32" cy="15" r="4.5" fill="#ffbd2e" />
  <circle cx="46" cy="15" r="4.5" fill="#27c93f" />

  <!-- Header Title -->
  <text x="{svg_w // 2}" y="19" text-anchor="middle" class="term-title">julianotx@github ~ ./contributions.sh --year</text>

  <!-- Month Axis Labels -->
  {"".join(months_svg)}

  <!-- Day Axis Labels -->
  {"".join(days_labels_svg)}

  <!-- Contribution Cells -->
  <g>
{"".join(cells_svg)}
  </g>

  <!-- Footer Stats (Left) -->
  <text x="{grid_left}" y="{leg_y + 9}" class="footer-stat">
    <tspan class="footer-stat-hl">{formatted_total}</tspan> contribuições no último ano • Streak Atual: <tspan class="footer-stat-hl">{current_streak} dias</tspan> • Recorde: <tspan class="footer-stat-hl">{longest_streak} dias</tspan>
  </text>

  <!-- Legend (Right) -->
  {"".join(legend_svg)}
</svg>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)

    print(f"[+] Heatmap SVG gerado com sucesso: {output_path} ({svg_w}x{svg_h})")

def main():
    json_path = sys.argv[1] if len(sys.argv) > 1 else "data/contributions.json"
    out_path = sys.argv[2] if len(sys.argv) > 2 else "contrib-heatmap.svg"
    data = load_data(json_path)
    render_heatmap(data, out_path)

if __name__ == "__main__":
    main()
