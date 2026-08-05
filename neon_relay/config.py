from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .contracts import WorkerSpec


@dataclass(frozen=True)
class RelayConfig:
    workers: tuple[WorkerSpec, ...]
    poll_seconds: int = 20
    github_repo: str = "crazytaxzi/Neon-Cortex"
    github_token_file: Path | None = None
    heavy_role: str = "heavy-review"
    max_snapshot_bytes: int = 180_000
    max_file_bytes: int = 40_000

    @classmethod
    def load(cls, path: Path) -> "RelayConfig":
        data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8-sig"))
        workers = tuple(WorkerSpec.from_dict(item) for item in data.get("workers", []))
        if not workers:
            raise ValueError("configuration must define at least one worker")
        token_file = data.get("github_token_file")
        resolved_token = None
        if token_file:
            resolved_token = Path(os.path.expandvars(str(token_file))).expanduser()
        return cls(
            workers=workers,
            poll_seconds=max(5, int(data.get("poll_seconds", 20))),
            github_repo=str(data.get("github_repo", "crazytaxzi/Neon-Cortex")),
            github_token_file=resolved_token,
            heavy_role=str(data.get("heavy_role", "heavy-review")),
            max_snapshot_bytes=max(10_000, int(data.get("max_snapshot_bytes", 180_000))),
            max_file_bytes=max(2_000, int(data.get("max_file_bytes", 40_000))),
        )

    def by_role(self, role: str) -> tuple[WorkerSpec, ...]:
        return tuple(worker for worker in self.workers if worker.role == role)
