# Changelog

## 0.1.1 — 2026-10-27

- Security: `dashmotion`'s `mode` value is normalized to `flow` or `architecture` before it is written into the generated HTML. A crafted value could previously inject script into the diagram page.

## 0.1.0 - 2026-10-27

First release. Skills only: no server, no network calls.

- `getting-started`: what the skills do, how to install them, and which one to use.
- `diagram`: editable draw.io files (`.drawio`, or `.drawio.svg` for a repo), with `scripts/check_drawio.py` to check structure.
- `network-diagram`: network topology diagrams from a device list the user supplies.
- `visualize`: a codebase map as one interactive HTML page, with real gaps listed.
- `dashmotion` 2.2.4 (credited, MIT): animated flow and architecture diagrams.
- `architecture-diagram` (credited, MIT): dark architecture diagrams as HTML.
