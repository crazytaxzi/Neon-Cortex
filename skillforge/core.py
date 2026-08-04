from __future__ import annotations

import json
import re
import shutil
from pathlib import Path


SKILL_TEMPLATE = """# {name}

## Purpose
{description}

## Trigger
Describe the conditions that should activate this skill.

## Inputs
List the required and optional inputs.

## Procedure
1. Replace this placeholder with the first deterministic step.
2. Add validation and failure handling.
3. Report evidence instead of claiming unverified success.

## Outputs
Describe the files, structured data, or user-facing result produced by the skill.

## Safety
Document confirmation requirements, destructive operations, secrets, and rollback behavior.

## Validation
Document the checks that prove the skill worked.
"""

README_TEMPLATE = """# {name}

{description}

The canonical instructions are in [SKILL.md](SKILL.md). Metadata is in
[manifest.json](manifest.json). Put automated checks in `tests/` and worked
examples in `examples/`.
"""


def slugify(name: str) -> str:
    """Convert a human-readable skill name into a safe kebab-case slug."""
    slug = re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")
    if not slug:
        raise ValueError("Skill name must contain at least one letter or number")
    return slug


def create_skill(
    name: str,
    description: str = "A new Neon Cortex skill",
    *,
    root: str | Path = "skills",
) -> Path:
    """Create a canonical Neon Cortex skill package without overwriting files."""
    slug = slugify(name)
    skill_dir = Path(root) / slug
    if skill_dir.exists():
        raise FileExistsError(f"Skill directory already exists: {skill_dir}")

    manifest = {
        "name": name.strip(),
        "slug": slug,
        "version": "0.1.0",
        "description": description.strip(),
        "entrypoint": "SKILL.md",
        "triggers": [],
        "requires_confirmation": [],
    }

    try:
        (skill_dir / "tests").mkdir(parents=True, exist_ok=False)
        (skill_dir / "examples").mkdir(exist_ok=False)
        (skill_dir / "SKILL.md").write_text(
            SKILL_TEMPLATE.format(name=name.strip(), description=description.strip()),
            encoding="utf-8",
        )
        (skill_dir / "README.md").write_text(
            README_TEMPLATE.format(name=name.strip(), description=description.strip()),
            encoding="utf-8",
        )
        (skill_dir / "manifest.json").write_text(
            json.dumps(manifest, indent=2) + "\n",
            encoding="utf-8",
        )
    except Exception:
        shutil.rmtree(skill_dir, ignore_errors=True)
        raise

    return skill_dir


def validate_skill(path: str | Path) -> list[str]:
    """Return validation errors for a skill directory; an empty list means valid."""
    skill_dir = Path(path)
    errors: list[str] = []

    for required in ("SKILL.md", "README.md", "manifest.json", "tests", "examples"):
        if not (skill_dir / required).exists():
            errors.append(f"Missing required path: {required}")

    manifest_path = skill_dir / "manifest.json"
    if manifest_path.is_file():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"Invalid manifest.json: {exc}")
        else:
            for key in ("name", "slug", "version", "description", "entrypoint"):
                if not manifest.get(key):
                    errors.append(f"manifest.json missing value: {key}")
            if manifest.get("slug") and manifest["slug"] != skill_dir.name:
                errors.append("manifest slug does not match directory name")
            if manifest.get("entrypoint") and not (skill_dir / manifest["entrypoint"]).is_file():
                errors.append("manifest entrypoint does not exist")

    return errors
