# SkillForge

SkillForge creates and validates the canonical Neon Cortex skill package:

```text
skills/<kebab-case-name>/
  SKILL.md
  README.md
  manifest.json
  tests/
  examples/
```

## Create a skill

```powershell
python -m skillforge create "Memory Audit" --description "Checks durable memory records"
```

## Validate a skill

```powershell
python -m skillforge validate skills/memory-audit
```

## Python API

```python
from skillforge import create_skill, slugify, validate_skill
```

SkillForge refuses to overwrite an existing skill and removes partial output if
file creation fails.
