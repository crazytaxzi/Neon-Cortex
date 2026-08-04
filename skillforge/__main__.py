#!/usr/bin/env python3
"""
SkillForge – a simple utility to generate a new skill package for the Neon‑Cortex agent ecosystem.

The tool creates the standard directory layout expected by the project:

```
.skills/
└── <skill-slug>/
    ├── SKILL.md
    ├── README.md
    └── ... (optional additional files)
```

The generated `SKILL.md` contains a minimal, well‑documented template that can be edited by the user to add trigger rules, steps, and any auxiliary files.

Usage:
    python -m skillforge <skill-name> [--description "…"]

The command writes the new skill under the current working directory. If the target directory already exists, the tool fails with a clear message to avoid accidental overwrites.
"""

import argparse
import os
import sys
from pathlib import Path

SKILL_TEMPLATE = """# {name}

## Description
{description}

## Trigger
* TODO – Define the trigger that activates this skill.

## Steps
1. TODO – Outline the steps the skill will perform.

## Outputs
* TODO – Describe the outputs or side‑effects.

---

**Notes**
* Keep the skill self‑contained. All required resources should live under the skill directory.
* The skill can be executed by the agent framework by referencing its path: `.skills/{slug}/SKILL.md`.
"""

README_TEMPLATE = """# {name}

This skill implements **{name}**.

- **Description**: {description}
- **Trigger**: TBD
- **Steps**: TBD
- **Outputs**: TBD

## Usage

Refer to the [SKILL.md](SKILL.md) for detailed instructions.
"""


def slugify(name: str) -> str:
    return name.strip().replace(' ', '-').lower()


def create_skill(name: str, description: str) -> Path:
    slug = slugify(name)
    skill_dir = Path('.skills') / slug
    if skill_dir.exists():
        raise FileExistsError(f'Skill directory {skill_dir} already exists')
    skill_dir.mkdir(parents=True, exist_ok=False)
    # Write SKILL.md
    skill_md = skill_dir / 'SKILL.md'
    skill_md.write_text(SKILL_TEMPLATE.format(name=name, description=description))
    # Write README.md
    readme_md = skill_dir / 'README.md'
    readme_md.write_text(README_TEMPLATE.format(name=name, description=description))
    return skill_dir


def main():
    parser = argparse.ArgumentParser(description='Generate a new skill package')
    parser.add_argument('name', help='Human‑friendly skill name')
    parser.add_argument('--description', default='A new skill', help='Short description of the skill')
    args = parser.parse_args()
    try:
        skill_dir = create_skill(args.name, args.description)
    except FileExistsError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    print(f'Skill created at {skill_dir.resolve()}')

if __name__ == '__main__':
    main()
