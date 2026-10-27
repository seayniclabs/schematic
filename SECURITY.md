# Security policy

## Reporting a vulnerability

Report it privately on GitHub: open the repository's **Security** tab and choose **Report a vulnerability**. Please don't open a public issue.

We acknowledge reports within 2 business days and aim to ship a fix for confirmed high-severity issues within 14 days. We credit reporters in the release notes unless you ask us not to.

## What Schematic does and doesn't do

- It is skills only: Markdown instructions and the files they ship with. There is no server, no background process and no telemetry.
- The skills make no network calls. The `check_drawio.py` script reads the file you name and nothing else.
- A skill writes only the files you ask for. The `visualize` skill reads source files in the project you name and skips `.env` files and other secret stores.
- Generated HTML pages (`dashmotion`, `architecture-diagram`) load fonts and, for export, scripts from public CDNs when a browser opens them. Those pages were built to do so; each page's own code is inline.

## Supported versions

The latest minor release receives security fixes.
