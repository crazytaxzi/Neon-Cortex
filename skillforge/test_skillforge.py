import os
import shutil
import tempfile
import subprocess
from pathlib import Path

import pytest

# Ensure the skillforge module can be imported
import skillforge


def test_slugify():
    assert skillforge.slugify('Hello World') == 'hello-world'


def test_create_skill(tmp_path):
    # Temporarily change working directory
    cwd = Path.cwd()
    os.chdir(tmp_path)
    try:
        skill_dir = skillforge.create_skill('Test Skill', 'A test skill')
        assert skill_dir.exists()
        assert (skill_dir / 'SKILL.md').exists()
        assert (skill_dir / 'README.md').exists()
        # Ensure content contains placeholders
        skill_md = (skill_dir / 'SKILL.md').read_text()
        assert 'Test Skill' in skill_md
        assert 'A test skill' in skill_md
    finally:
        os.chdir(cwd)


def test_prevent_overwrite(tmp_path):
    cwd = Path.cwd()
    os.chdir(tmp_path)
    try:
        skillforge.create_skill('Dup Skill', 'First')
        with pytest.raises(FileExistsError):
            skillforge.create_skill('Dup Skill', 'Second')
    finally:
        os.chdir(cwd)


def test_cli(tmp_path):
    cwd = Path.cwd()
    os.chdir(tmp_path)
    try:
        result = subprocess.run(['python', '-m', 'skillforge', 'CLI Skill', '--description', 'CLI test'], capture_output=True, text=True)
        assert result.returncode == 0
        assert 'Skill created at' in result.stdout
        skill_dir = Path('.skills') / 'cli-skill'
        assert skill_dir.exists()
        assert (skill_dir / 'SKILL.md').exists()
    finally:
        os.chdir(cwd)
