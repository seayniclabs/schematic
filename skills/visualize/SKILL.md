---
name: visualize
description: Map a codebase into one self-contained interactive HTML page showing its components, how they connect, where data flows, and which external services it calls. Also lists real gaps such as orphaned files and dead endpoints. Use when the user wants to see how an unfamiliar project fits together, asks for an architecture or component map, or wants to find unused or unprotected code.
license: MIT
source: https://github.com/seayniclabs/schematic
author: Seaynic Labs
---

# Visualize a codebase

Read a project's source and produce `component-map.html`: a dark, interactive force-directed graph you open in a browser. The map is derived from the code, so regenerate it when the code changes instead of keeping an old copy.

## 1. Confirm the project

Use the path the user gave. If they gave none, ask for one. Confirm it is a source tree. If it has no source code (only notes or documents), say so and suggest the diagram skill instead.

Detect the framework from its signals:

| Signal | Framework |
|---|---|
| `astro.config.*` | Astro |
| `next.config.*` | Next.js |
| `express` or `fastify` in `package.json` | Node server |
| `Package.swift` or `*.xcodeproj` | Swift or SwiftUI |
| MCP SDK imports and tool registrations | MCP server |
| `docker-compose.yml` only | Docker or infrastructure |

Read the README if there is one. It tells you what the project is for, which helps you judge what is intended and what is dead code.

## 2. Find the components

Use Glob and Grep. Record every discrete unit with a type, a short label (the file name, not the full path), and its file path.

| Type | What to look for |
|---|---|
| Page or route | `pages/`, `app/` route files, route definitions |
| API endpoint | `api/` handlers, `@Get`/`@Post` decorators, `app.get(` calls |
| UI component | `components/`, `.vue`, `.svelte`, React components |
| Layout | `layouts/`, wrapper components |
| Middleware | `middleware.*`, auth guards, request interceptors |
| Service | Service classes, API clients, integrations |
| Model | Data types, schemas, ORM models |
| Database | Migrations, schema files, query code |
| Worker | Cron jobs, queue consumers, background tasks |
| Config | Environment loading, feature flags |
| MCP tool, resource, prompt | `server.tool(`, `server.resource(`, `server.prompt(` registrations |
| Swift view or view model | `struct X: View`, `@Observable` classes |

## 3. Find the relationships

Record each one as a directed edge: A depends on B, not "A and B are related".

- Imports and requires between modules
- Calls from one module into another
- Fetch or HTTP calls to internal endpoints
- Middleware order
- Which services read or write which models
- Environment variables that point at other services

Mark an edge as an external call when it goes outside the project: a third-party API, an identity provider, another service's URL. Name the external service and the component that calls it.

## 4. Find the real gaps

Report only gaps that exist in this code. A false positive costs more trust than a missed minor gap.

| Gap | How to check |
|---|---|
| Orphaned file | Nothing imports or references it, and it is not an entry point |
| Dead endpoint | An API route with no caller in the project |
| Unprotected route | A route that skips the auth middleware the other routes use |
| Missing validation | An endpoint that reads input with no schema or check |
| Circular dependency | A imports B and B imports A, directly or through a short chain |
| Undocumented external | An outbound call to a host that no config or env var mentions |
| Unhandled async path | An `await` or promise chain with no catch and no caller that handles errors |

Give each gap a severity: high (security or data loss), medium (broken behavior), low (cleanup).

## 5. Write the page

Write one self-contained `component-map.html`: inline CSS, the data as an inline JSON object, and D3 v7 loaded from cdnjs:

```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script>
```

Write it to the path the user gave, or to `component-map.html` in the current directory. Do not write into any other folder, and do not store the map anywhere else.

Node colors:

| Type | Color | Shape |
|---|---|---|
| Page or route | `#60a5fa` | Rectangle |
| API endpoint, MCP tool | `#34d399` | Rectangle |
| UI component | `#a78bfa` | Rectangle |
| Layout | `#818cf8` | Rectangle |
| Middleware | `#fbbf24` | Diamond |
| Service | `#f472b6` | Rectangle |
| Model | `#94a3b8` | Rounded rectangle |
| Database | `#38bdf8` | Cylinder |
| External service | `#fb923c` | Dashed border |
| Config | `#d4d4d8` | Small rectangle |
| Worker | `#c084fc` | Hexagon |

Edges: imports solid, API calls dashed, data flow thick, middleware dotted, external calls orange dashed.

Behavior:

- Hover a node: highlight it and its edges, dim the rest.
- Click a node: a side panel with the file path, type, incoming and outgoing edges, and any gap.
- Drag nodes, zoom and pan.
- Toggle buttons in the header filter by node type.
- Nodes with gaps get a red ring. The sidebar lists the gaps, grouped by severity, and must match the rings.
- Header shows the project name, framework, generation time, and counts of components, connections and gaps.
- Footer reads "Generated by the visualize skill".

Force settings: `forceLink` distance by edge type, `forceManyBody` with negative charge, `forceCenter`, `forceCollide` to stop overlaps, and `forceX`/`forceY` to cluster nodes by type. For more than 100 components, group by directory first and let the user expand a group.

Keep the page readable on a dark background: text contrast of at least 4.5:1.

## 6. Check and report

Open the page in a browser if you have a browser tool, and confirm the console shows no errors. Check that the JSON data parses. Report:

- The path to `component-map.html`
- Counts: components, connections, gaps
- The top three gaps, with file paths
- Anything the code shows that contradicts the project's README

## Safety

- Read source files only. Do not run the project, install its dependencies or call its services.
- Skip `.env` files and anything that looks like a secret store. Never print a secret's value; mention that the file exists if it matters.
- The map is a snapshot. Say so in the report.
