#!/usr/bin/env python3
"""Fail if a skill could ship without its license or its credit.

Every skills/<name>/SKILL.md needs `name`, `description`, `license` and `source` in its
frontmatter. A skill whose source is not this repository is third-party: it must keep a
LICENSE file in its folder, use a permissive license, and be listed in CREDITS.md.
The repository URL comes from the "repository" field of .claude-plugin/plugin.json.
Usage: python scripts/check_skills.py   (exit 0 = all good)
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PERMISSIVE = {"MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "CC-BY-4.0", "CC0-1.0", "ISC"}


def front(text: str) -> dict[str, str]:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    meta = {}
    for line in (m.group(1).splitlines() if m else []):
        if line and not line[0].isspace() and ":" in line:
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip()
    return meta


def main() -> int:
    own = None
    manifest = ROOT / ".claude-plugin" / "plugin.json"
    if manifest.exists():
        repo = json.loads(manifest.read_text(encoding="utf-8")).get("repository")
        own = repo.rstrip("/") if isinstance(repo, str) and repo else None
    credits = (ROOT / "CREDITS.md").read_text() if (ROOT / "CREDITS.md").exists() else ""
    problems = []
    skills = sorted((ROOT / "skills").glob("*/SKILL.md"))
    if not skills:
        problems.append("no skills/<name>/SKILL.md found")
    for path in skills:
        name = path.parent.name
        meta = front(path.read_text(encoding="utf-8"))
        for key in ("name", "description", "license", "source"):
            if not meta.get(key):
                problems.append(f"{name}: frontmatter is missing `{key}`")
        if meta.get("license") and meta["license"] not in PERMISSIVE:
            problems.append(f"{name}: license {meta['license']!r} is not on the permissive list")
        third_party = own is None or not meta.get("source", "").startswith(own)
        if third_party:
            if not any(p.name.upper().startswith(("LICENSE", "LICENCE")) for p in path.parent.iterdir()):
                problems.append(f"{name}: third-party skill without a LICENSE file in its folder")
            if f"`{name}`" not in credits:
                problems.append(f"{name}: third-party skill not listed in CREDITS.md")
    for p in problems:
        print(p)
    print(f"check_skills: {len(skills)} skill(s), {len(problems)} problem(s)", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
