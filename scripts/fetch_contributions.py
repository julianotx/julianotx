#!/usr/bin/env python3
"""
scripts/fetch_contributions.py
Busca as contribuições públicas de https://github.com/users/julianotx/contributions
Sem token e sem GraphQL.
Salva data/contributions.json com:
- Lista de dias brutos (data, contagem, nível)
- Estatísticas derivadas: streak atual, streak mais longo, melhor dia, total do último ano e totais mensais.
"""

import os
import sys
import json
import re
from datetime import datetime, timezone
from pathlib import Path
import requests
from bs4 import BeautifulSoup

USER = "julianotx"
CONTRIBUTIONS_URL = f"https://github.com/users/{USER}/contributions"
OUTPUT_FILE = Path("data/contributions.json")

def fetch_contributions_html():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    print(f"[*] Requisitando contribuições de {CONTRIBUTIONS_URL}...")
    response = requests.get(CONTRIBUTIONS_URL, headers=headers, timeout=15)
    response.raise_for_status()
    return response.text

def parse_contributions(html_text: str):
    soup = BeautifulSoup(html_text, "html.parser")
    tooltips = {t["for"]: t.get_text(strip=True) for t in soup.find_all("tool-tip") if t.has_attr("for")}
    
    day_cells = soup.find_all("td", class_="ContributionCalendar-day")
    if not day_cells:
        day_cells = soup.find_all("rect", class_="ContributionCalendar-day")

    days_data = []
    for cell in day_cells:
        date_str = cell.get("data-date")
        if not date_str:
            continue
        
        level = int(cell.get("data-level", 0))
        cell_id = cell.get("id", "")
        tt_text = tooltips.get(cell_id, "")

        count_match = re.search(r"(\d+)\s+contribution", tt_text)
        count = int(count_match.group(1)) if count_match else 0
        
        days_data.append({
            "date": date_str,
            "count": count,
            "level": level
        })

    days_data.sort(key=lambda x: x["date"])
    return days_data

def calculate_stats(days_data: list):
    if not days_data:
        return {
            "total": 0,
            "current_streak": 0,
            "longest_streak": 0,
            "best_day": {"date": None, "count": 0},
            "monthly_totals": {}
        }

    total = sum(d["count"] for d in days_data)
    
    # Melhor dia
    best = max(days_data, key=lambda x: x["count"])
    best_day = {"date": best["date"], "count": best["count"]}

    # Streak mais longo e atual
    longest_streak = 0
    cur_run = 0
    for d in days_data:
        if d["count"] > 0:
            cur_run += 1
            if cur_run > longest_streak:
                longest_streak = cur_run
        else:
            cur_run = 0

    # Streak atual (contando a partir do final)
    current_streak = 0
    for d in reversed(days_data):
        if d["count"] > 0:
            current_streak += 1
        elif current_streak > 0:
            break

    # Totais mensais
    monthly = {}
    for d in days_data:
        ym = d["date"][:7]
        monthly[ym] = monthly.get(ym, 0) + d["count"]

    return {
        "total": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "monthly_totals": monthly
    }

def main():
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    html_text = fetch_contributions_html()
    days = parse_contributions(html_text)
    stats = calculate_stats(days)

    payload = {
        "user": USER,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "total_days": len(days),
        "stats": stats,
        "days": days
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    print(f"[+] Contribuições salvas com sucesso em {OUTPUT_FILE}:")
    print(f"    - Total no último ano: {stats['total']}")
    print(f"    - Streak Atual: {stats['current_streak']} dias")
    print(f"    - Streak Mais Longo: {stats['longest_streak']} dias")
    print(f"    - Melhor Dia: {stats['best_day']['date']} ({stats['best_day']['count']} contribuições)")

if __name__ == "__main__":
    main()
