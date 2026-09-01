# Isherveer Bhullar — Portfolio

Personal portfolio site, hosted on GitHub Pages: **https://codemastervy.github.io**

## Pages

| File | Section |
|---|---|
| `index.html` | About |
| `resume.html` | Resume |
| `videos.html` | Videos |
| `projects.html` | Projects |
| `credentials.html` | Credentials |
| `contact.html` | Contact |

Each page shares `style.css` (all styling and light/dark theme) and `script.js` (theme toggle, clock, filter buttons).

## Editing

This is plain HTML, no build step. To update something:

1. Open the relevant `.html` file and edit the content inside `<section class="panel active">`.
2. Commit and push to `main`.
3. GitHub Pages rebuilds automatically, usually within a minute.

To add a new video, copy an existing `.v-card` block in `videos.html` and swap in the new Google Drive file ID (`https://drive.google.com/file/d/FILE_ID/preview`) and title.

To add a new project, copy an existing `.project-card` block in `projects.html`. Add a `<a class="repo-link" href="...">View on GitHub →</a>` line once the matching repo is public.

## Automated project sync

`projects.html` is not only edited by hand — `.github/workflows/sync-projects.yml` runs `scripts/sync_projects.py` on a daily cron (and can be triggered manually via `workflow_dispatch`). Each run:

1. Calls the GitHub API for all public, non-fork repos under `codemastervy` (skipping this repo itself).
2. Compares that list against the repo names already linked from `projects.html` (found by regexing existing `github.com/codemastervy/<name>"` links).
3. For each repo not yet listed, generates a new `.project-card` block (title-cased name, description or a fallback line, creation date, up to 3 tags from topics/language) and inserts it right before the project grid's closing `</div></div></section>` markup.
4. Updates the "Everything N" filter button count to match the new total card count.
5. If anything changed, commits `projects.html` directly to `main` as `github-actions[bot]` and pushes — no PR is opened.

Implications for anyone editing this repo:

- Publishing a new public repo on GitHub is often enough on its own to make a project card appear here within a day, with no edit to this repo required.
- The script matches the grid's closing markup as a literal string (`GRID_CLOSE` in `scripts/sync_projects.py`) to know where to insert cards. If `projects.html`'s structure around the closing `</section>` of the project grid changes, the script will raise `SystemExit` instead of silently misplacing cards — so a manual restructure of that section should be paired with a check that the workflow still runs (`gh workflow run sync-projects.yml` or `python3 scripts/sync_projects.py` locally).
- To keep a real repo off the Projects page (e.g. this site's own repo), add its name to `SKIP_REPOS` in `scripts/sync_projects.py`.

