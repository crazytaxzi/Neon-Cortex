from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path

from .contracts import CommandResult, JobContract


_TEXT_EXTENSIONS = {
    ".py", ".ps1", ".cmd", ".bat", ".json", ".toml", ".yaml", ".yml",
    ".md", ".txt", ".html", ".css", ".js", ".ts", ".tsx", ".jsx",
}
_SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache", "dist", "build"}


class Workspace:
    def __init__(self, root: Path, max_snapshot_bytes: int, max_file_bytes: int):
        self.root = root.resolve()
        self.max_snapshot_bytes = max_snapshot_bytes
        self.max_file_bytes = max_file_bytes

    def run(self, argv: tuple[str, ...], timeout: int = 300) -> CommandResult:
        started = time.perf_counter()
        completed = subprocess.run(
            list(argv),
            cwd=self.root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            shell=False,
        )
        return CommandResult(argv, completed.returncode, completed.stdout, completed.stderr, time.perf_counter() - started)

    def git(self, *args: str, timeout: int = 300) -> CommandResult:
        return self.run(("git", *args), timeout=timeout)

    def ensure_clean(self) -> None:
        result = self.git("status", "--porcelain")
        if result.exit_code != 0:
            raise RuntimeError(result.stderr or "git status failed")
        if result.stdout.strip():
            raise RuntimeError("workspace has uncommitted changes; relay refuses to mix its work with yours")

    def create_branch(self, task_id: str) -> str:
        safe = "".join(ch.lower() if ch.isalnum() else "-" for ch in task_id).strip("-") or "task"
        branch = f"relay/{safe}"
        existing = self.git("branch", "--list", branch)
        result = self.git("checkout", branch) if existing.stdout.strip() else self.git("checkout", "-b", branch)
        if result.exit_code != 0:
            raise RuntimeError(result.stderr or "could not create relay branch")
        return branch

    def snapshot(self, job: JobContract) -> str:
        parts: list[str] = []
        used = 0
        explicit = {Path(item).as_posix() for item in job.context_files}
        for base, dirs, files in os.walk(self.root):
            dirs[:] = [d for d in dirs if d not in _SKIP_DIRS]
            for name in sorted(files):
                path = Path(base) / name
                rel = path.relative_to(self.root).as_posix()
                if explicit and rel not in explicit:
                    continue
                if not explicit and path.suffix.lower() not in _TEXT_EXTENSIONS:
                    continue
                try:
                    size = path.stat().st_size
                except OSError:
                    continue
                if size > self.max_file_bytes or used + size > self.max_snapshot_bytes:
                    continue
                try:
                    text = path.read_text(encoding="utf-8")
                except (UnicodeDecodeError, OSError):
                    continue
                parts.append(f"\n--- FILE: {rel} ---\n{text}")
                used += size
        return "".join(parts)

    def apply_patch(self, patch_text: str) -> None:
        patch = self._extract_patch(patch_text)
        if not patch.strip():
            raise RuntimeError("worker returned no unified diff")
        if "../" in patch or "..\\" in patch:
            raise RuntimeError("patch attempts to escape the workspace")
        patch_file = self.root / ".neon-relay.patch"
        patch_file.write_text(patch, encoding="utf-8")
        try:
            check = self.git("apply", "--check", str(patch_file))
            if check.exit_code != 0:
                raise RuntimeError(check.stderr or "git apply --check failed")
            apply = self.git("apply", str(patch_file))
            if apply.exit_code != 0:
                raise RuntimeError(apply.stderr or "git apply failed")
        finally:
            patch_file.unlink(missing_ok=True)

    @staticmethod
    def _extract_patch(text: str) -> str:
        marker = "```diff"
        if marker in text:
            body = text.split(marker, 1)[1]
            return body.split("```", 1)[0].strip() + "\n"
        start = text.find("diff --git ")
        return text[start:] if start >= 0 else text

    def commit(self, task_id: str, goal: str) -> str:
        add = self.git("add", "-A")
        if add.exit_code != 0:
            raise RuntimeError(add.stderr or "git add failed")
        diff = self.git("diff", "--cached", "--quiet")
        if diff.exit_code == 0:
            raise RuntimeError("worker produced no repository changes")
        message = f"relay({task_id}): {goal[:68]}"
        commit = self.git("commit", "-m", message)
        if commit.exit_code != 0:
            raise RuntimeError(commit.stderr or "git commit failed")
        sha = self.git("rev-parse", "HEAD")
        if sha.exit_code != 0:
            raise RuntimeError(sha.stderr or "could not read commit SHA")
        return sha.stdout.strip()
