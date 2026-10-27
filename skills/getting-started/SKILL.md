---
name: getting-started
description: Orient a new user of the Schematic skills. Explains what they do, how to install them in Claude Code as a plugin or by copying the skills folder into another app, which skill fits which request, and how to open the files they produce. Use when the user asks what Schematic is, how to install or start with these skills, or which diagram skill to use.
license: MIT
source: https://github.com/seayniclabs/schematic
author: Seaynic Labs
---

# Getting started with Schematic

Schematic is a set of skills that let an AI assistant draw diagrams as files the user can open, edit and commit. It has no server and no background process. Each skill writes only the files the user asks for.

## What the skills produce

| You ask for | Skill | File you get |
|---|---|---|
| A flowchart, sequence, swimlane, ER or architecture diagram you can edit | `diagram` | `.drawio`, or `.drawio.svg` for a repo |
| A network map from a device list | `network-diagram` | `.drawio` or `.drawio.svg`, plus a device table |
| A map of how a codebase fits together, with gaps | `visualize` | `component-map.html` you open in a browser |
| An animated diagram with moving connectors or requests | `dashmotion` | a self-contained `.html` file |
| A dark architecture diagram for a landing page or deck | `architecture-diagram` | a self-contained `.html` file |

Pick the static editable format (`diagram`) when the user will edit it. Pick the animated one (`dashmotion`) when the diagram is for showing, not editing.

## Install

### As a Claude Code plugin

In Claude Code, run these two commands:

```
/plugin marketplace add seayniclabs/plugins
/plugin install schematic@seayniclabs
```

The skills then load in every project. Start a new session if they do not appear.

### In any app that reads Agent Skills

Copy the `skills/` folder from the repository into the app's skills folder. Keep each skill's folder intact, including its `LICENSE` file and its `scripts/` folder. Check the app's documentation for where it keeps skills.

Each skill is a folder with a `SKILL.md` file. The app reads the `name` and `description` lines to decide when to use it, so no other setup is needed.

## Which skill to use

- The user wants to edit the diagram later, or keep it in git: `diagram`.
- The user has a device list and wants a network map: `network-diagram`.
- The user wants to understand an unfamiliar codebase: `visualize`.
- The user wants motion (requests flowing, data moving) for a README, landing page or demo: `dashmotion`.
- The user wants a polished dark architecture image as a web page: `architecture-diagram`.

If two fit, ask the user which they want before you start.

## Open the files

- `.drawio` files: draw.io desktop, the web app at app.diagrams.net, or VS Code with the draw.io extension.
- `.drawio.svg` files: GitHub shows them as images in READMEs and docs. draw.io also opens them for editing.
- `.html` files: double-click them, or open them in any browser. They work offline except for fonts and scripts loaded from a CDN when the page opens.

## Check a draw.io file

The `diagram` skill includes `scripts/check_drawio.py`. It needs only Python 3:

```bash
python3 <skills-folder>/diagram/scripts/check_drawio.py <file.drawio>
```

It reports broken connections, overlapping shapes and malformed files, and exits 0 when the file is clean.

## First five minutes

1. Ask for one diagram you know well, such as your own service's request path.
2. Read the file in draw.io. Move one box to check that the layout holds up.
3. Ask for a change in plain words ("add a cache between the API and the database"). The skill edits the file rather than starting over.
4. Commit the `.drawio.svg` next to the README that uses it.
