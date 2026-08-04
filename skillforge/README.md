# SkillForge

SkillForge is a small utility that generates a ready‑to‑use skill package for the Neon‑Cortex agent framework.

## Features

- Creates the standard directory layout under `.skills/<slug>/`.
- Generates a minimal `SKILL.md` template with placeholders for trigger, steps, and outputs.
- Generates a `README.md` that gives a quick overview.
- Prevents accidental overwrite of an existing skill.
- Can be used via the command line (`python -m skillforge <name> [--description <text>]`) or imported as a Python library.

## Usage

```bash
$ python -m skillforge "My Example Skill" --description "A simple example"
Skill created at /path/to/project/.skills/my-example-skill
```

The new skill will be available at `.skills/my-example-skill/`.

## API

```python
from skillforge import create_skill, slugify

# Create a skill programmatically
skill_dir = create_skill("My Skill", "Description")
print(skill_dir)
```

## License

MIT – see the repository license.
