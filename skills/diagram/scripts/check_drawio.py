#!/usr/bin/env python3
"""Check a draw.io diagram file for structural problems. Standard library only.

Works on .drawio files and on .drawio.svg files (the diagram is read from the
svg's draw.io `content` attribute). Checks, per page:

  - the file is well-formed XML and the root is <mxfile> (or <mxGraphModel>)
  - every <diagram> has an <mxGraphModel> with a <root>; compressed pages are decoded
  - every cell id is unique
  - every vertex has an mxGeometry
  - every edge has a source and a target, and both exist
  - no two vertices with the same parent overlap (any area shared by more than
    1px in both directions). Containment inside a container is fine because the
    child has a different parent.

Usage:  python3 check_drawio.py FILE [FILE ...]
Exit:   0 = clean, 1 = problems found, 2 = a file could not be read or parsed.
"""

from __future__ import annotations

import base64
import sys
import urllib.parse
import xml.etree.ElementTree as ET
import zlib
from pathlib import Path

TOLERANCE = 1.0  # px; smaller overlaps are treated as touching


def load_mxfile(path: Path) -> ET.Element:
    root = ET.fromstring(path.read_bytes())
    if root.tag.split("}")[-1] == "svg":
        content = root.get("content")
        if content is None:
            raise ValueError("SVG has no draw.io `content` attribute; re-export with 'Include a copy of my diagram'")
        root = ET.fromstring(content)
    return root


def decode_page(text: str) -> ET.Element:
    """A compressed <diagram> holds base64(raw deflate(URL-encoded mxGraphModel))."""
    raw = zlib.decompress(base64.b64decode(text), -15)
    return ET.fromstring(urllib.parse.unquote(raw.decode("utf-8")))


def pages(mxfile: ET.Element):
    if mxfile.tag == "mxGraphModel":
        yield "(single page)", mxfile
        return
    if mxfile.tag != "mxfile":
        raise ValueError(f"root element is <{mxfile.tag}>, expected <mxfile>")
    diagrams = mxfile.findall("diagram")
    if not diagrams:
        raise ValueError("no <diagram> element")
    for d in diagrams:
        name = d.get("name") or d.get("id") or "?"
        model = d.find("mxGraphModel")
        if model is None:
            text = (d.text or "").strip()
            if not text:
                raise ValueError(f"page {name!r} has no mxGraphModel")
            model = decode_page(text)
        yield name, model


def rect(cell: ET.Element):
    g = cell.find("mxGeometry")
    if g is None:
        return None
    try:
        return tuple(float(g.get(k, "0")) for k in ("x", "y", "width", "height"))
    except ValueError:
        return None


def overlap(a, b) -> bool:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    w = min(ax + aw, bx + bw) - max(ax, bx)
    h = min(ay + ah, by + bh) - max(ay, by)
    return w > TOLERANCE and h > TOLERANCE


def check_page(name: str, model: ET.Element) -> tuple[list[str], int, int]:
    problems: list[str] = []
    root = model.find("root")
    if root is None:
        return [f"page {name!r}: no <root> in mxGraphModel"], 0, 0

    holder = {child: el for el in root.iter() for child in el}
    ids: dict[str, ET.Element] = {}
    cells: list[tuple[str, ET.Element]] = []
    for cell in root.iter("mxCell"):
        owner = holder.get(cell)
        cid = cell.get("id") or (owner.get("id") if owner is not None and owner.tag != "root" else None)
        if not cid:
            problems.append(f"page {name!r}: a cell has no id")
            continue
        if cid in ids:
            problems.append(f"page {name!r}: duplicate cell id {cid!r}")
        ids[cid] = cell
        cells.append((cid, cell))

    vertices = [(cid, c) for cid, c in cells if c.get("vertex") == "1"]
    edges = [(cid, c) for cid, c in cells if c.get("edge") == "1"]

    by_parent: dict[str, list[tuple[str, tuple]]] = {}
    for cid, cell in vertices:
        r = rect(cell)
        if r is None:
            problems.append(f"page {name!r}: vertex {cid!r} has no mxGeometry")
            continue
        by_parent.setdefault(cell.get("parent", "1"), []).append((cid, r))

    for siblings in by_parent.values():
        for i, (ida, ra) in enumerate(siblings):
            for idb, rb in siblings[i + 1:]:
                if overlap(ra, rb):
                    problems.append(f"page {name!r}: vertices {ida!r} and {idb!r} overlap")

    for cid, cell in edges:
        for end in ("source", "target"):
            ref = cell.get(end)
            if not ref:
                problems.append(f"page {name!r}: edge {cid!r} has no {end}")
            elif ref not in ids:
                problems.append(f"page {name!r}: edge {cid!r} {end} {ref!r} does not exist")

    return problems, len(vertices), len(edges)


def check_file(path: Path) -> tuple[int, list[str]]:
    """Return (exit code for this file, lines to print)."""
    try:
        mxfile = load_mxfile(path)
        results = [(name, *check_page(name, model)) for name, model in pages(mxfile)]
    except (OSError, ET.ParseError, ValueError, zlib.error) as exc:
        return 2, [f"{path}: cannot read: {exc}"]

    lines = []
    total_v = sum(r[2] for r in results)
    total_e = sum(r[3] for r in results)
    problems = [f"{path}: {p}" for _, probs, _, _ in results for p in probs]
    if problems:
        return 1, problems
    lines.append(f"OK {path}: {len(results)} page(s), {total_v} vertices, {total_e} edges")
    return 0, lines


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0 if argv else 2
    status = 0
    for arg in argv:
        code, lines = check_file(Path(arg))
        for line in lines:
            print(line)
        status = max(status, code)
    return status


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
