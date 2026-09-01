#!/usr/bin/env python3
"""
scripts/fetch_github_stats.py
Fetches public GitHub profile stats for julianotx via the GitHub REST API.
Saves data/github_stats.json with: public_repos, followers, following,
stars_given, total_stars_received, top_languages.
No auth token required (public API).
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path
import requests

USER = "julianotx"
API_BASE = "https://api.github.com"
OUTPUT = Path("data/github_stats.json")
HEADERS = {
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "julianotx-profile-readme/1.0",
}


def fetch_stats():
    # User info
    print(f"[*] Fetching profile stats for {USER}...")
    r = requests.get(f"{API_BASE}/users/{USER}", headers=HEADERS, timeout=10)
    r.raise_for_status()
    user = r.json()

    public_repos = user.get("public_repos", 0)
    followers = user.get("followers", 0)
    following = user.get("following", 0)

    # Stars given (count via pagination)
    r2 = requests.get(
        f"{API_BASE}/users/{USER}/starred?per_page=1",
        headers=HEADERS, timeout=10
    )
    stars_given = 0
    link = r2.headers.get("Link", "")
    m = re.search(r'page=(\d+)>; rel="last"', link)
    if m:
        stars_given = int(m.group(1))
    elif r2.status_code == 200 and r2.json():
        stars_given = len(r2.json())

    # Repos: stars received + languages
    r3 = requests.get(
        f"{API_BASE}/users/{USER}/repos?per_page=100&sort=updated",
        headers=HEADERS, timeout=10
    )
    repos = r3.json() if r3.status_code == 200 else []
    total_stars = sum(repo.get("stargazers_count", 0) for repo in repos)

    langs = {}
    for repo in repos:
        lang = repo.get("language")
        if lang:
            langs[lang] = langs.get(lang, 0) + 1
    top_languages = sorted(langs.items(), key=lambda x: -x[1])

    payload = {
        "user": USER,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "public_repos": public_repos,
        "followers": followers,
        "following": following,
        "stars_given": stars_given,
        "total_stars_received": total_stars,
        "top_languages": top_languages,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    print(f"[+] GitHub stats saved to {OUTPUT}:")
    print(f"    Repos: {public_repos} | Followers: {followers} | "
          f"Stars Given: {stars_given} | Stars Received: {total_stars}")
    print(f"    Top Languages: {top_languages[:5]}")


if __name__ == "__main__":
    fetch_stats()
