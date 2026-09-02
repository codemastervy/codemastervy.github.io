#!/usr/bin/env python3
"""Add a project card to projects.html for any public repo not already listed.

Run by .github/workflows/sync-projects.yml. Safe to run manually too:
    python3 scripts/sync_projects.py
"""
import json
import os
import re
import urllib.request
from pathlib import Path

USERNAME = "codemastervy"
SKIP_REPOS = {"codemastervy", "codemastervy.github.io"}
PROJECTS_FILE = Path(__file__).resolve().parent.parent / "projects.html"
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

GRID_CLOSE = "        </div>\n      </div>\n    </section>"


def fetch_repos():
    headers = {"Accept": "application/vnd.github+json", "User-Agent": USERNAME}
    # Authenticated requests get a 5,000/hour rate limit tied to this repo's
    # token instead of the 60/hour limit shared by every unauthenticated
    # caller on GitHub's runner IPs.
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(
        f"https://api.github.com/users/{USERNAME}/repos?per_page=100&sort=created",
        headers=headers,
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def existing_repo_names(html):
    return set(re.findall(rf'github\.com/{USERNAME}/([\w.-]+)"', html))


def format_date(created_at):
    year, month = created_at[:4], int(created_at[5:7])
    return f"{MONTHS[month - 1]} {year} to Present"


def title_case(name):
    return re.sub(r"[-_]+", " ", name).title()


def infer_category(repo):
    """Pick the filter bucket a new repo belongs in.

    The filter buttons on projects.html are driven by each card's
    data-category, so a card without one is invisible to every filter except
    "Everything". Matched against topics first (they're deliberate), then
    language, then a default of "systems" -- the safest bucket, since an
    uncategorised repo here is far more often infrastructure than an app.
    """
    topics = {t.lower() for t in (repo.get("topics") or [])}
    language = (repo.get("language") or "").lower()

    media_signals = {"video", "video-editing", "design", "obs", "streaming",
                     "photography", "drone", "audio"}
    app_signals = {"ios", "macos", "swift", "swiftui", "android", "app",
                   "game", "gamedev", "unity", "flutter", "react-native"}
    leadership_signals = {"leadership", "teaching", "mentoring", "community"}

    if topics & leadership_signals:
        return "leadership"
    if topics & media_signals:
        return "media"
    if topics & app_signals:
        return "app-dev"
    if language in {"swift", "kotlin", "dart", "c#", "objective-c"}:
        return "app-dev"
    return "systems"


def build_card(repo):
    name = repo["name"]
    title = title_case(name)
    desc = repo["description"] or f"See the {name} repository on GitHub for details."
    date = format_date(repo["created_at"])
    tags = repo.get("topics") or ([repo["language"]] if repo.get("language") else [])
    tags = tags[:3] or ["Project"]
    chips = "".join(
        f'<span class="chip">{title_case(t)}</span>' for t in tags
    )
    # data-autogen marks this card as safe to refresh on a later run. Cards
    # without it have been written or edited by hand -- several of those have
    # much better copy than the repo's one-line GitHub description, so a
    # blanket description sync would actively downgrade the page.
    return (
        f'          <div class="project-card" data-category="{infer_category(repo)}" data-autogen="true">\n'
        f'            <div class="project-thumb"></div>\n'
        f'            <h4>{title}</h4>\n'
        f'            <div class="project-date">{date}</div>\n'
        f'            <p>{desc}</p>\n'
        f'            <div class="chip-row">{chips}</div>\n'
        f'            <a class="repo-link" href="https://github.com/{USERNAME}/{name}" '
        f'target="_blank" rel="noopener">View on GitHub →</a>\n'
        f'          </div>\n'
    )


CARD_RE = re.compile(
    r'<div class="project-card"(?P<attrs>[^>]*)>(?P<body>.*?)\n          </div>\n',
    re.DOTALL,
)


def refresh_autogen_cards(html, repos_by_name):
    """Bring script-generated cards back in line with their repo metadata.

    Scoped to data-autogen cards on purpose: a description improved on GitHub
    should reach the site, but hand-curated copy must never be clobbered.
    """
    updated = []

    def replace(match):
        attrs, body = match.group("attrs"), match.group("body")
        if 'data-autogen="true"' not in attrs:
            return match.group(0)
        m = re.search(rf'github\.com/{USERNAME}/([\w.-]+)"', body)
        if not m:
            return match.group(0)
        repo = repos_by_name.get(m.group(1))
        if not repo:
            return match.group(0)

        new_body = body
        desc = repo["description"] or f"See the {repo['name']} repository on GitHub for details."
        new_body = re.sub(r"<p>.*?</p>", f"<p>{desc}</p>", new_body, count=1, flags=re.DOTALL)
        tags = (repo.get("topics") or ([repo["language"]] if repo.get("language") else []))[:3] or ["Project"]
        chips = "".join(f'<span class="chip">{title_case(t)}</span>' for t in tags)
        new_body = re.sub(
            r'<div class="chip-row">.*?</div>',
            f'<div class="chip-row">{chips}</div>',
            new_body, count=1, flags=re.DOTALL,
        )
        # Category can change as topics are added to a repo over time.
        new_attrs = re.sub(
            r'data-category="[^"]*"',
            f'data-category="{infer_category(repo)}"',
            attrs, count=1,
        )
        if new_body != body or new_attrs != attrs:
            updated.append(repo["name"])
        return f'<div class="project-card"{new_attrs}>{new_body}\n          </div>\n'

    return CARD_RE.sub(replace, html), updated


def sync_filter_counts(html):
    """Recompute every filter badge from the cards actually on the page.

    The old version only rewrote "Everything", so the other four badges drifted
    and had stopped adding up: they read 3/3/2/1 against a grid of 12 cards.
    The front-end recomputes these at runtime too; keeping the markup correct
    means the page is right before any JavaScript runs.
    """
    categories = re.findall(r'<div class="project-card"[^>]*data-category="([^"]+)"', html)
    total = html.count('<div class="project-card"')

    def repl(match):
        head, filt, label, _old = match.group(1), match.group(2), match.group(3), match.group(4)
        n = total if filt == "all" else categories.count(filt)
        return f'{head}data-filter="{filt}">{label}<span class="filter-count">{n}</span>'

    return re.sub(
        r'(<button class="filter-btn(?: active)?" )data-filter="([^"]+)">([^<]*)<span class="filter-count">(\d+)</span>',
        repl,
        html,
    )


def main():
    original = PROJECTS_FILE.read_text(encoding="utf-8")
    html = original
    known = existing_repo_names(html)

    repos = fetch_repos()
    repos_by_name = {r["name"]: r for r in repos}
    new_repos = [
        r for r in repos
        if not r["fork"] and r["name"] not in SKIP_REPOS and r["name"] not in known
    ]

    if new_repos:
        cards = "".join(build_card(r) for r in new_repos)
        if GRID_CLOSE not in html:
            raise SystemExit("Could not find the project-grid closing anchor. "
                             "projects.html structure may have changed — update GRID_CLOSE.")
        html = html.replace(GRID_CLOSE, cards + GRID_CLOSE, 1)
        print(f"Added {len(new_repos)} project card(s): "
              + ", ".join(r["name"] for r in new_repos))
    else:
        print("No new repos to add.")

    html, refreshed = refresh_autogen_cards(html, repos_by_name)
    if refreshed:
        print(f"Refreshed {len(refreshed)} auto-generated card(s): " + ", ".join(refreshed))

    # Always run, even when nothing was added: the badges could already be
    # stale from an earlier version of this script, and a hand-added card
    # needs counting too.
    html = sync_filter_counts(html)

    if html == original:
        print("projects.html already up to date.")
        return

    PROJECTS_FILE.write_text(html, encoding="utf-8")
    counts = re.findall(
        r'data-filter="([^"]+)">[^<]*<span class="filter-count">(\d+)</span>', html)
    print("Filter counts now: " + ", ".join(f"{f}={n}" for f, n in counts))


if __name__ == "__main__":
    main()
