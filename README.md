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

