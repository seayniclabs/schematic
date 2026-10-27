---
name: diagram
description: Create an editable draw.io diagram from a plain description. Writes a .drawio file, or a .drawio.svg when the diagram belongs in a repo next to its docs. Covers flowcharts, architecture, sequence, swimlane, ER and org diagrams. Use when the user asks for a diagram they can edit in draw.io or diagrams.net, or for a diagram to commit with a README. For an animated diagram use the dashmotion skill.
license: MIT
source: https://github.com/seayniclabs/schematic
author: Seaynic Labs
---

# Diagram (draw.io)

Turn a description into a draw.io file the user can open, edit and version. The output is plain XML that draw.io, diagrams.net and VS Code's draw.io extension all open.

## 1. Pick the output format

| The user wants | Write | Why |
|---|---|---|
| A diagram to edit in draw.io, or a standalone file | `<name>.drawio` | Smallest and simplest |
| A diagram in a repo, shown in a README or docs | `<name>.drawio.svg` | GitHub renders it as an image, and draw.io still opens it for editing |

For `.drawio.svg`, the file is an SVG with two parts:

1. The root `<svg>` has a `content` attribute holding the complete `<mxfile>` XML, with `"`, `<`, `&` escaped as `&quot;`, `&lt;`, `&amp;`. This is the source of truth.
2. The visible drawing: the same shapes and edges as plain SVG (`<rect>`, `<text>`, `<path>` with an arrow `<marker>`), computed from the same `mxGeometry` values. Set `width`, `height` and `viewBox` from the page size (`pageWidth`, `pageHeight`).

Write the `.drawio` XML first, then derive the SVG from it so the two never disagree.

If the user does not say, write `.drawio`. Name the file after the title: lowercase, hyphens, no special characters ("Network Topology" becomes `network-topology.drawio`). If the file already exists, ask before overwriting.

## 2. Plan the diagram

List every shape, its label, every connection with its direction and label, and any grouping (container, swimlane, zone). Pick one flow direction (top to bottom or left to right) and stick to it. For more than 15 shapes, split into pages (section 6).

## 3. Write the XML

Every file has this skeleton. The two mandatory cells come first.

```xml
<mxfile host="Claude" modified="2026-01-01T00:00:00.000Z" agent="Claude" version="24.0.0" type="device">
  <diagram id="page-1" name="Overview">
    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1100" pageHeight="850" background="#ffffff" math="0" shadow="0">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <!-- vertices and edges, all with parent="1" unless inside a container -->
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

### Vertices

```xml
<mxCell id="web_frontend" value="Web frontend" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1">
  <mxGeometry x="120" y="80" width="140" height="60" as="geometry"/>
</mxCell>
```

### Edges

```xml
<mxCell id="edge_web_to_api" value="HTTPS" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=classic;labelBackgroundColor=#ffffff;" edge="1" parent="1" source="web_frontend" target="api_gateway">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>
```

Every edge needs `source` and `target` that match existing vertex ids. Add waypoints with `<Array as="points"><mxPoint x="..." y="..."/></Array>` inside the edge's mxGeometry when a route must avoid a shape.

### Containers and groups

Children use the container's id as `parent`, and their x and y are relative to the container's top-left corner.

```xml
<mxCell id="zone_private" value="Private subnet" style="swimlane;whiteSpace=wrap;html=1;startSize=30;fillColor=#f5f5f5;strokeColor=#666666;" vertex="1" parent="1">
  <mxGeometry x="300" y="60" width="400" height="260" as="geometry"/>
</mxCell>
<mxCell id="svc_orders" value="Orders" style="whiteSpace=wrap;html=1;rounded=1;" vertex="1" parent="zone_private">
  <mxGeometry x="30" y="60" width="120" height="60" as="geometry"/>
</mxCell>
```

Use a swimlane when the diagram shows who owns each step. Use a plain group (`group;`) for a loose visual grouping.

### Ids

Use descriptive ids (`svc_orders`, `edge_orders_to_db`), never bare numbers. Every id is unique within its page, and pages are independent.

## 4. Shapes and style

Base style strings (add colors and text settings as needed):

| Shape | Style |
|---|---|
| Rectangle | `whiteSpace=wrap;html=1;` |
| Rounded rectangle | `rounded=1;whiteSpace=wrap;html=1;arcSize=10;` |
| Ellipse | `shape=ellipse;whiteSpace=wrap;html=1;` |
| Decision | `shape=rhombus;whiteSpace=wrap;html=1;` |
| Terminator (start/end) | `rounded=1;whiteSpace=wrap;html=1;arcSize=50;` |
| Database | `shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;size=15;` |
| Cloud | `shape=cloud;whiteSpace=wrap;html=1;` |
| Document | `shape=document;whiteSpace=wrap;html=1;` |
| Actor | `shape=mxgraph.basic.person;whiteSpace=wrap;html=1;` |
| Swimlane | `swimlane;whiteSpace=wrap;html=1;startSize=30;` |
| Dashed frame | `whiteSpace=wrap;html=1;fillColor=none;strokeColor=#666666;dashed=1;` |

Edges:

| Type | Style |
|---|---|
| Straight arrow | `endArrow=classic;html=1;` |
| Orthogonal | `edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=classic;` |
| Curved | `curved=1;html=1;endArrow=classic;` |
| Dashed | `dashed=1;html=1;endArrow=classic;` |
| Two-way | `endArrow=classic;startArrow=classic;html=1;` |
| Entity relation | `edgeStyle=entityRelationEdgeStyle;html=1;endArrow=ERmany;startArrow=ERone;` |

Use orthogonal edges for architecture and network diagrams, straight edges for simple flowcharts.

Palette (fill / stroke), one palette per diagram, at most four or five colors:

| Role | Fill | Stroke |
|---|---|---|
| Primary | `#dae8fc` | `#6c8ebf` |
| Success | `#d5e8d4` | `#82b366` |
| Warning | `#fff2cc` | `#d6b656` |
| Danger | `#f8cecc` | `#b85450` |
| Neutral | `#f5f5f5` | `#666666` |

Set `fontColor=#333333` on light fills. Text in labels is short; use `html=1` with `<br>` only for a second line, and escape markup inside `value` (`&lt;b&gt;Title&lt;/b&gt;`).

## 5. Layout

- Snap every x and y to a multiple of 10.
- Keep at least 40px between shapes, and 80 to 120px between columns and rows.
- Typical sizes: rectangle 120x60, decision 80x80, database 60x80, cloud 120x80.
- Align shapes by their centers.
- Prefer swimlanes when ownership matters.

## 6. Multiple pages

Put an overview on the first page and detail on the others. Each `<diagram>` has its own `<mxGraphModel>` with its own cells 0 and 1.

## 7. Check the file, then report

Run the bundled checker before you report. Use the path to this skill's folder:

```bash
python3 <this-skill-folder>/scripts/check_drawio.py <file>
```

It checks that the XML is well formed, every edge's source and target exist, every vertex has a geometry, ids are unique, and no two shapes with the same parent overlap. It exits 0 when clean, 1 when there are problems, and 2 when it cannot read the file. Fix every problem it reports and run it again. The checker needs only Python 3.

Then report the file path as a link and one line on what it shows. Do not open the file yourself.

## Notes

- A `.drawio` file is plain XML and diffs cleanly in git.
- Open it in draw.io desktop, at app.diagrams.net, or in VS Code with the draw.io extension.
- Use this skill for a static, editable diagram. For a diagram where data visibly moves, use the dashmotion skill.
