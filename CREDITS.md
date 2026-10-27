# Credits

Schematic is made by [Seaynic Labs](https://seayniclabs.com) and released under the MIT license.

It includes skills written by others, used under their licenses. Each skill folder keeps its original `LICENSE` file. We added `license:` and `source:` lines to each skill's frontmatter and left the rest as published. Copied on 2026-10-27 from the commits linked below.

| Skill | Author | License | Source |
|---|---|---|---|
| `dashmotion` | Mars (csthink) | MIT | [csthink/dashmotion @ ae2fe4f](https://github.com/csthink/dashmotion/tree/ae2fe4f28c60caa53da8b15fa3537f4ea576f4ad/skills/dashmotion) |
| `architecture-diagram` | Cocoon AI | MIT | [Cocoon-AI/architecture-diagram-generator @ 4b9087d](https://github.com/Cocoon-AI/architecture-diagram-generator/tree/4b9087d55268c79a935105439dbcd37b630fc3f3/architecture-diagram) |

Copyright notices: `dashmotion`, Copyright (c) 2026 Mars (csthink). `architecture-diagram`, Copyright (c) 2025 Cocoon AI.

Skills by Seaynic Labs: `getting-started`, `diagram`, `network-diagram`, `visualize`.

## Changes we made to credited skills

- `dashmotion/scripts/layout.py`: the diagram `mode` is normalized to `flow` or `architecture` before it is written into the generated HTML (it was inserted unescaped). Reported upstream: https://github.com/csthink/dashmotion/issues/3
