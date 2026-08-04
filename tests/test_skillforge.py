from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from skillforge import create_skill, slugify, validate_skill


def test_slugify() -> None:
    assert slugify("Hello, World!") == "hello-world"
    with pytest.raises(ValueError):
        slugify("---")


def test_create_and_validate_skill(tmp_path: Path) -> None:
    skill_dir = create_skill("Test Skill", "A test skill", root=tmp_path / "skills")

    assert skill_dir == tmp_path / "skills" / "test-skill"
    assert validate_skill(skill_dir) == []
    assert (skill_dir / "tests").is_dir()
    assert (skill_dir / "examples").is_dir()

    manifest = json.loads((skill_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["slug"] == "test-skill"
    assert manifest["entrypoint"] == "SKILL.md"


def test_prevent_overwrite(tmp_path: Path) -> None:
    root = tmp_path / "skills"
    create_skill("Duplicate", root=root)
    with pytest.raises(FileExistsError):
        create_skill("Duplicate", root=root)


def test_validation_reports_missing_paths(tmp_path: Path) -> None:
    skill_dir = tmp_path / "broken"
    skill_dir.mkdir()
    errors = validate_skill(skill_dir)
    assert "Missing required path: SKILL.md" in errors
    assert "Missing required path: manifest.json" in errors


def test_cli_create_and_validate(tmp_path: Path) -> None:
    root = tmp_path / "skills"
    create_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "skillforge",
            "create",
            "CLI Skill",
            "--description",
            "CLI test",
            "--root",
            str(root),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert create_result.returncode == 0, create_result.stderr or create_result.stdout

    skill_dir = root / "cli-skill"
    validate_result = subprocess.run(
        [sys.executable, "-m", "skillforge", "validate", str(skill_dir)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert validate_result.returncode == 0, validate_result.stderr or validate_result.stdout
